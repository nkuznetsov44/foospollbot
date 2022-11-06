from contextlib import contextmanager
from uuid import uuid4
from aiogram.types.message import Message, ContentType
from aiogram.types.update import Update

from app import dp, storage, start_app
from settings import settings
from models.entities import TelegramUser, UserInfo, UserState
from filters import NewUserFilter, UserStateFilter
from state_machine import UserStateMachine
from parsers import PhoneParser, RtsfUrlParser
from exceptions import (
    EvksPlayerDoesNotExist,
    PhoneParseError,
    RtsfUrlParseError,
    TelegramUserDoesNotExist,
)
from logger import get_logger


logger = get_logger()

PHOTO_STORAGE_PATH = settings["photo_storage_path"]
ORG_TELEGRAM_USER = settings["org_telegram_user"]


@contextmanager
def enrich_logs(handler_name: str, message: Message) -> None:
    with logger:
        logger.context_push(
            handler=handler_name,
            telegram_user_id=message.from_user.id,
            message=message.text,
        )
        yield


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
    with enrich_logs('collect_photo_no_content', message):
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
        await message.photo[-1].download(destination_file=f"{PHOTO_STORAGE_PATH}/{photo_id}.jpg")

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


@dp.message_handler(UserStateFilter(UserState.IN_REVIEW))
async def in_review_handler(message: Message) -> None:
    with enrich_logs("in_review", message):
        logger.info("IN_REVIEW_STATUS_POLLED")
        await message.answer(text="Ваша заявка на проверке. Ждите результатов.")


@dp.errors_handler(exception=Exception)
async def exception_handler(update: Update, exception: Exception) -> None:
    with enrich_logs("exception", update.message):
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
        }.get(type(exception))
        if not msg:
            logger.exception("UNEXPECTED_ERROR")
            msg = "Произошла неизвестная ошибка. Обратитесь к оргинизаторам."
        await update.message.answer(msg)
        return True


if __name__ == "__main__":
    start_app()
