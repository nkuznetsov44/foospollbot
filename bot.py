import logging
from aiogram.types.message import Message
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

from app import dp, storage, start_app
from models.entities import TelegramUser, UserInfo, UserState
from filters import UserStateFilter
from state_machine import UserStateMachine
from parsers import PhoneParser, RtsfUrlParser
from exceptions import EvksPlayerAlreadyRegistered, EvksPlayerDoesNotExist, ParseError


logger = logging.getLogger(__name__)


@dp.message_handler(commands='start')
async def start_handler(message: Message) -> None:
    user_info = UserInfo(
        id=None,
        telegram_user_id=message.from_user.id,
        state=UserStateMachine.get_initial_state(),
    )

    telegram_user = TelegramUser(
        id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        user_info=user_info
    )

    async with storage.session() as session:
        session.add(telegram_user)
        session.add(user_info)
        await session.commit()

    await message.answer(text='Сообщите свое имя')


@dp.message_handler(UserStateFilter(UserState.COLLECTING_FIRST_NAME))
async def collect_first_name_handler(message: Message) -> None:
    first_name = message.text.strip()

    async with storage.session() as session:
        telegram_user = await storage.get_telegram_user_by_id(session, message.from_user.id)
        user_info = telegram_user.user_info
        user_sm = UserStateMachine(user_info.state)

        user_info.first_name = first_name
        user_sm.next()
        user_info.state = user_sm.state

        session.add(user_info)
        await session.commit()

    await message.answer(text='Сообщите свою фамилию')


@dp.message_handler(UserStateFilter(UserState.COLLECTING_LAST_NAME))
async def collect_last_name_handler(message: Message) -> None:
    last_name = message.text.strip()

    async with storage.session() as session:
        telegram_user = await storage.get_telegram_user_by_id(session, message.from_user.id)
        user_info = telegram_user.user_info
        user_sm = UserStateMachine(user_info.state)

        user_info.last_name = last_name
        user_sm.next()
        user_info.state = user_sm.state

        session.add(user_info)
        await session.commit()

    await message.answer(text='Сообщите номер телефона')


@dp.message_handler(UserStateFilter(UserState.COLLECTING_PHONE))
async def collect_phone_handler(message: Message) -> None:
    try:
        phone = PhoneParser(message.text).parse()

        async with storage.session() as session:
            telegram_user = await storage.get_telegram_user_by_id(session, message.from_user.id)
            user_info = telegram_user.user_info
            user_sm = UserStateMachine(user_info.state)

            user_info.phone = phone
            user_sm.next()
            user_info.state = user_sm.state

            session.add(user_info)
            await session.commit()

        await message.answer(text='Пришлите ссылку на свой рейтинг на https://rtsf.ru/ratings')
    except ParseError:
        await message.answer('Номер телефона невалидный. Попробуйте указать его снова.')
        raise


@dp.message_handler(UserStateFilter(UserState.COLLECTING_RTSF_URL))
async def collect_rtsf_url_handler(message) -> None:
    try:
        parsed_url = RtsfUrlParser(message.text).parse()
        async with storage.session() as session:
            telegram_user = await storage.get_telegram_user_by_id(session, message.from_user.id)
            user_info = telegram_user.user_info
            evks_player = await storage.get_evks_player_by_id(session, parsed_url.evks_player_id)
            user_sm = UserStateMachine(user_info.state)

            user_info.rtsf_url = parsed_url.url
            user_info.evks_player = evks_player
            user_sm.next()
            user_info.state = user_sm.state

            session.add(user_info)
            await session.commit()
        await message.answer(text='Заявка создана. Она будет проверена вручную. Ждите результатов.')
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            await message.answer(
                'Участник рейтинга уже зарегистирирован. Пожалуйста, обратитесь к организаторам.'
            )
            raise EvksPlayerAlreadyRegistered(evks_player_id=parsed_url.evks_player_id) from e
    except EvksPlayerDoesNotExist:
        await message.answer(
            'Ссылка на рейтинг указывает на несуществующего игрока. Если вы уверены, что '
            'все правильно, напишите, пожалуйста, оргинизаторам.'
        )
        raise
    except ParseError:
        await message.answer(
            'Ссылка на рейтинг невалидная. Она должна вести на профиль игрока, '
            'например https://rtsf.ru/player/175. Попробуйте снова.'
        )
        raise


if __name__ == '__main__':
    start_app()
