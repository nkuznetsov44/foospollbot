from contextlib import contextmanager
from uuid import uuid4
import string
import secrets
from aiogram.types.message import Message
from aiogram.types.update import Update
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import (
    ContentType,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from aiogram.dispatcher.filters.builtin import IDFilter, Text
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from transitions import MachineError

from app import bot, dp, storage, start_app
from settings import settings
from models.entities import (
    TelegramUser,
    UserInfo,
    UserState,
    VoteResult,
)
from filters import NewUserFilter, UserStateFilter
from state_machine import UserStateMachine
from parsers import PhoneParser, RtsfUrlParser
from exceptions import (
    EvksPlayerDoesNotExist,
    PhoneParseError,
    RtsfUrlParseError,
    TelegramUserDoesNotExist,
    UserStateMachineError,
)
from logger import get_logger
from poll_sender import AbstractPollSender, VoteOptionCallback


logger = get_logger()


PHOTO_STORAGE_PATH = settings["photo_storage_path"]
ORG_TELEGRAM_USER = settings["org_telegram_user"]
ADMIN_CHAT_ID = settings["admin_chat_id"]


ApproveCallback = CallbackData("APPROVE", "telegram_user_id")
RejectCallback = CallbackData("REJECT", "telegram_user_id")


class PollSender(AbstractPollSender):
    bot = bot
    storage = storage


def generate_secret_code(len: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(len)).upper()


@contextmanager
def enrich_logs(handler_name: str, message: Message) -> None:
    with logger:
        logger.context_push(
            handler=handler_name,
            telegram_user_id=message.from_user.id,
            message=message.text,
        )
        yield


@dp.message_handler(
    IDFilter(chat_id=ADMIN_CHAT_ID),
    Text(equals="/startvote"),
)
async def admin_handler_startvote(message: Message) -> None:
    async with storage.session() as session:
        user_ids = await storage.get_accepted_users(session)
        vote_options = await storage.get_vote_options(session)

    sender = PollSender(user_ids, options=tuple(vote_options))
    await message.answer("Началась отправка опросов")
    await sender.send()
    await message.answer("Отправка опросов закончена")


@dp.message_handler(
    IDFilter(chat_id=ADMIN_CHAT_ID),
    Text(equals="/info"),
)
async def admin_handler_info(message: Message) -> None:
    async with storage.session() as session:
        info = await storage.get_info(session)
        text = "*States:*\n"
        for state, count in info["states"].items():
            text += f"{state.value}: {count}\n"

        text += "\n*Current results:*\n"
        for option, count in info["results"].items():
            text += f"{option}: {count}\n"

        await message.answer(
            text=text.replace("_", "\\_"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


@dp.callback_query_handler(VoteOptionCallback.filter())
async def vote_result_handler(
    callback: CallbackQuery, callback_data: dict[str, str]
) -> None:
    with logger:
        logger.context_push(
            handler="vote_result",
            telegram_user_id=callback.from_user.id,
            data=callback_data,
        )
        logger.info("RECEIVED_VOTE_RESULT")

        try:
            option_id = int(callback_data["option_id"])

            async with storage.session() as session:
                user_info = await storage.get_user_info(
                    session=session,
                    telegram_user_id=callback.from_user.id,
                    for_update=True,
                )
                user_sm = UserStateMachine(user_info.state)
                user_sm.vote_result(user_info)
                user_info.state = user_sm.state
                session.add(user_info)

                secret_code = generate_secret_code()
                vote_result = VoteResult(
                    id=None,
                    telegram_user_id=user_info.telegram_user_id,
                    selected_option_id=option_id,
                    secret_code=secret_code,
                )
                session.add(vote_result)

                selected_option = await storage.get_vote_option(session, option_id)

                await session.commit()

            logger.context_push(secret_code=secret_code)
            logger.info("SAVED_VOTE_RESULT")
        except MachineError:
            logger.exception("VOTE_RESULT_STATE_ERROR")
            await bot.send_message(
                chat_id=callback.from_user.id,
                text="Ваш запрос обрабатывается, бот может отвечать "
                "с задержкой из-за большого количества запросов. "
                "Если вы все-таки не получили подтверждения "
                "о том, что ваш голос принят, напишите "
                f"организаторам @{ORG_TELEGRAM_USER}.",
            )
        else:
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=(
                    f"Ваш голос за кандидата *{selected_option.text}* учтен.\n"
                    f"`{secret_code}`\n"
                    "это ваш уникальный код. Не показывайте его никому, "
                    "его знаете только вы, он обеспечивает анонимность и "
                    "прозрачность голосования. Вместе с результатами голосования "
                    "будет опубликовано соответствие секретных кодов и вариантов, "
                    "которые выбрали владельцы кода. Так вы сможете убедиться, "
                    "что ваш голос не потерялся и был учтен правильно."
                )
                .replace(".", "\\."),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info("VOTE_CODE_NOTIFICATION_SENT")
        finally:
            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except MessageNotModified:
                logger.warn("MESSAGE_NOT_MODIFIED_ERROR", exc_info=True)


@dp.callback_query_handler(IDFilter(chat_id=ADMIN_CHAT_ID), ApproveCallback.filter())
async def approve_handler(
    callback: CallbackQuery, callback_data: dict[str, str]
) -> None:
    with logger:
        logger.context_push(
            handler="approve_handler",
            callback_data=callback_data,
            from_user=callback.from_user.as_json(),
        )
        logger.info("APPROVE_USER_REQUEST")

        try:
            telegram_user_id = int(callback_data["telegram_user_id"])
            async with storage.session() as session:
                user_info = await storage.get_user_info(
                    session=session,
                    telegram_user_id=telegram_user_id,
                    for_update=True,
                )
                user_sm = UserStateMachine(user_info.state)
                user_sm.approve(user_info)
                user_info.state = user_sm.state
                session.add(user_info)
                await session.commit()

            logger.info("APPROVED_USER")

            await notify_approved(telegram_user_id)
            logger.info("APPROVE_NOTIFICATION_SENT")

            await callback.message.reply(
                text=f"Approved by @{callback.from_user.username}"
            )
        except MachineError as me:
            raise UserStateMachineError(message=me.value)
        finally:
            try:
                await callback.message.edit_reply_markup(reply_markup=None)
            except MessageNotModified:
                logger.warn("MESSAGE_NOT_MODIFIED_ERROR", exc_info=True)


@dp.callback_query_handler(IDFilter(chat_id=ADMIN_CHAT_ID), RejectCallback.filter())
async def reject_handler(
    callback: CallbackQuery, callback_data: dict[str, str]
) -> None:
    with logger:
        logger.context_push(
            handler="approve_handler",
            callback_data=callback_data,
            from_user=callback.from_user.as_json(),
        )
        logger.info("REJECT_USER_REQUEST")

        telegram_user_id = int(callback_data["telegram_user_id"])
        async with storage.session() as session:
            user_info = await storage.get_user_info(
                session=session,
                telegram_user_id=telegram_user_id,
                for_update=True,
            )
            user_sm = UserStateMachine(user_info.state)
            user_sm.reject(user_info)
            user_info.state = user_sm.state
            session.add(user_info)
            await session.commit()

        logger.info("REJECTED_USER")

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(text=f"Rejected by @{callback.from_user.username}")


@dp.message_handler(NewUserFilter())
async def new_user_handler(message: Message) -> None:
    with enrich_logs("new_user", message):
        logger.info("NEW_USER")

        async with storage.session() as session:
            try:
                telegram_user = await storage.get_telegram_user(
                    session, message.from_user.id
                )
            except TelegramUserDoesNotExist:
                telegram_user = TelegramUser(
                    id=message.from_user.id,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    username=message.from_user.username,
                )
                session.add(telegram_user)
                user_info = UserInfo(
                    id=None,
                    telegram_user_id=message.from_user.id,
                    state=UserStateMachine.get_initial_state(),
                )
                session.add(user_info)
                await session.commit()
                logger.info("USER_CREATED")
            else:
                logger.warning("USER_ALREADY_EXISTS_SKIP_CREATING")

        await message.answer(text="Сообщите свое имя")


@dp.message_handler(UserStateFilter(UserState.COLLECTING_FIRST_NAME))
async def collect_first_name_handler(message: Message) -> None:
    with enrich_logs("collect_first_name", message):
        logger.info("COLLECTING_FIRST_NAME")

        first_name = message.text.strip()

        async with storage.session() as session:
            user_info = await storage.get_user_info(
                session=session,
                telegram_user_id=message.from_user.id,
                for_update=True,
            )
            user_sm = UserStateMachine(user_info.state)

            user_info.first_name = first_name
            user_sm.next()
            user_info.state = user_sm.state

            session.add(user_info)
            await session.commit()

        logger.info("SAVED_FIRST_NAME")
        await message.answer(text="Сообщите свою фамилию")


@dp.message_handler(UserStateFilter(UserState.COLLECTING_LAST_NAME))
async def collect_last_name_handler(message: Message) -> None:
    with enrich_logs("collect_last_name", message):
        logger.info("COLLECTING_LAST_NAME")

        last_name = message.text.strip()

        async with storage.session() as session:
            user_info = await storage.get_user_info(
                session=session,
                telegram_user_id=message.from_user.id,
                for_update=True,
            )
            user_sm = UserStateMachine(user_info.state)

            user_info.last_name = last_name
            user_sm.next()
            user_info.state = user_sm.state

            session.add(user_info)
            await session.commit()

        logger.info("SAVED_LAST_NAME")
        await message.answer(text="Сообщите номер телефона")


@dp.message_handler(UserStateFilter(UserState.COLLECTING_PHONE))
async def collect_phone_handler(message: Message) -> None:
    with enrich_logs("collect_phone", message):
        logger.info("COLLECTING_PHONE")

        phone = PhoneParser(message.text).parse()

        async with storage.session() as session:
            user_info = await storage.get_user_info(
                session=session,
                telegram_user_id=message.from_user.id,
                for_update=True,
            )
            user_sm = UserStateMachine(user_info.state)

            user_info.phone = phone
            user_sm.next()
            user_info.state = user_sm.state

            session.add(user_info)
            await session.commit()

        logger.info("SAVED_PHONE")
        await message.answer(
            text="Пришлите ссылку на свой рейтинг на https://rtsf.ru/ratings"
        )


@dp.message_handler(UserStateFilter(UserState.COLLECTING_RTSF_URL))
async def collect_rtsf_url_handler(message: Message) -> None:
    with enrich_logs("collect_rtsf_url", message):
        logger.info("COLLECTING_RTSF_URL")

        parsed_url = RtsfUrlParser(message.text).parse()
        async with storage.session() as session:
            user_info = await storage.get_user_info(
                session=session,
                telegram_user_id=message.from_user.id,
                for_update=True,
            )
            evks_player = await storage.get_evks_player(
                session, parsed_url.evks_player_id
            )
            user_sm = UserStateMachine(user_info.state)

            user_info.rtsf_url = parsed_url.url
            user_info.evks_player_id = evks_player.id
            user_sm.next()
            user_info.state = user_sm.state

            session.add(user_info)
            await session.commit()

        logger.info("SAVED_RTSF_URL")
        await message.answer(
            text=(
                "Мы очень хотим избежать фрода в голосовании, поэтому вынуждены "
                "попросить вас прислать селфи. Это последний этап регистрации."
            )
        )


@dp.message_handler(
    UserStateFilter(UserState.COLLECTING_PHOTO),
    content_types=(ContentType.TEXT,),
)
async def collect_photo_no_content_handler(message: Message) -> None:
    with enrich_logs("collect_photo_no_content", message):
        logger.info("NO_PHOTO_FOUND_IN_MESSAGE")
        await message.answer(text="Сообщение должно содержать фотографию.")


@dp.message_handler(
    UserStateFilter(UserState.COLLECTING_PHOTO),
    content_types=(ContentType.PHOTO,),
)
async def collect_photo_handler(message: Message) -> None:
    with enrich_logs("collect_photo", message):
        logger.info("COLLECTING_PHOTO")

        photo_id = uuid4()
        await message.photo[-1].download(
            destination_file=f"{PHOTO_STORAGE_PATH}/{photo_id}.jpg"
        )

        async with storage.session() as session:
            user_info = await storage.get_user_info(
                session=session,
                telegram_user_id=message.from_user.id,
                for_update=True,
            )
            user_sm = UserStateMachine(user_info.state)
            user_info.photo_id = photo_id
            user_sm.next()
            user_info.state = user_sm.state
            session.add(user_info)
            await session.commit()

        logger.context_push(photo_id=str(photo_id))
        logger.info("SAVED_PHOTO")

        await message.answer(
            text=(
                "Ваша заявка принята и будет рассмотрена вручную. Пожалуйста, "
                "не удаляйте этот чат. Когда придет время, бот пришлет вам опрос "
                f"для голосования. Если будут вопросы, пишите @{ORG_TELEGRAM_USER}"
            )
        )

        await notify_admins_review(message.from_user.id)
        logger.info("REVIEW_NOTIFICATION_SENT")


async def notify_admins_review(telegram_user_id: int) -> None:
    async with storage.session() as session:
        telegram_user = await storage.get_telegram_user(session, telegram_user_id)
        user_info = await storage.get_user_info(session, telegram_user_id)
        evks_player = await storage.get_evks_player(session, user_info.evks_player_id)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=(
                [
                    InlineKeyboardButton(
                        text="Approve",
                        callback_data=ApproveCallback.new(
                            telegram_user_id=telegram_user_id
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Reject",
                        callback_data=RejectCallback.new(
                            telegram_user_id=telegram_user_id
                        ),
                    )
                ],
            )
        )
        with open(f"{PHOTO_STORAGE_PATH}/{user_info.photo_id}.jpg", "rb") as photo:
            await bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo,
                caption=(
                    f"Telegram info: @{telegram_user.username} "
                    f"({telegram_user.first_name} {telegram_user.last_name})\n"
                    f"Real name: {user_info.last_name} {user_info.first_name}\n"
                    f"Phone: {user_info.phone}\n"
                    f"EVKS: {evks_player.last_name} {evks_player.first_name} "
                    f"{user_info.rtsf_url}\n"
                    f"Last competition: {evks_player.last_competition_date}"
                ),
                reply_markup=keyboard,
            )


async def notify_approved(telegram_user_id: int) -> None:
    await bot.send_message(
        chat_id=telegram_user_id,
        text=(
            "Ваша заявка одобрена. Пожалуйста, не удаляйте этот чат. "
            "Когда наступит время голосования вам придет опрос."
        ),
    )


@dp.message_handler(UserStateFilter(UserState.IN_REVIEW))
async def in_review_handler(message: Message) -> None:
    with enrich_logs("in_review", message):
        logger.info("IN_REVIEW_STATUS_POLLED")
        await message.answer(text="Ваша заявка на проверке. Ждите результатов.")


@dp.errors_handler(exception=Exception)
async def exception_handler(update: Update, exception: Exception) -> None:
    with logger:
        logger.context_push(
            update=update.as_json(),
            error=str(exception),
        )
        logger.info("EXCEPTION_FALLBACK_HANDLER")
        msg = {
            PhoneParseError: (
                "Не удалось сохранить номер телефона. "
                "Если вы уверены, что указали все правильно, "
                f"обратитесь к оргинизаторам @{ORG_TELEGRAM_USER} "
                "или попробуйте снова."
            ),
            RtsfUrlParseError: (
                "Ссылка на рейтинг невалидная. "
                "Она должна вести на профиль игрока, "
                "например https://rtsf.ru/ratings/player/175. "
                f"Обратитесь к оргинизаторам @{ORG_TELEGRAM_USER} "
                "или попробуйте снова."
            ),
            EvksPlayerDoesNotExist: (
                "Ссылка на рейтинг указывает на несуществующего игрока. "
                "Если вы уверены, что указали все правильно, "
                f"обратитесь к оргинизаторам @{ORG_TELEGRAM_USER} "
                "или попробуйте снова."
            ),
            UserStateMachineError: {f"Ошибка обновления состояния:\n{exception}"},
        }.get(type(exception))

        if not msg:
            logger.exception("UNEXPECTED_ERROR")
            msg = "Произошла неизвестная ошибка. Обратитесь к оргинизаторам."

        if update.message:
            await update.message.answer(msg)
        elif update.callback_query:
            await update.callback_query.message.answer(msg)
        else:
            logger.error("UNSUPPORTED_MESSAGE_TYPE")

        return True


if __name__ == "__main__":
    start_app()
