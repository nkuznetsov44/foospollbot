from aiogram.types.message import Message

from app import dp, storage, start_app
from models.entities import TelegramUser, UserInfo, UserState
from filters import UserStateFilter
from state_machine import UserStateMachine
from validators import PhoneValidator, RtsfUrlValidator


@dp.message_handler(commands='start')
async def start_handler(message: Message) -> None:
    telegram_user = TelegramUser(
        id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        user_info=UserInfo(
            state=UserStateMachine.get_initial_state(),
        )
    )

    async with storage.session() as session:
        session.add(telegram_user)
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
    phone = message.text.strip()
    if not PhoneValidator(phone).is_valid():
        await message.answer('Номер телефона невалидный. Попробуйте указать его снова.')

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


@dp.message_handler(UserStateFilter(UserState.COLLECTING_RTSF_URL))
async def collect_rtsf_url_handler(message) -> None:
    rtsf_url = message.text.strip()
    if not RtsfUrlValidator(rtsf_url).is_valid():
        await message.answer(
            'Ссылка на рейтинг невалидная. Она должна вести на профиль игрока '
            'на сайте https://rtsf.ru/ratings. Попробуйте снова.'
        )

    async with storage.session() as session:
        telegram_user = await storage.get_telegram_user_by_id(session, message.from_user.id)
        user_info = telegram_user.user_info
        user_sm = UserStateMachine(user_info.state)

        user_info.rtsf_url = rtsf_url
        user_sm.next()
        user_info.state = user_sm.state

        session.add(user_info)
        await session.commit()

    await message.answer(text='Заявка создана. Она будет проверена вручную. Ждите результатов.')


if __name__ == '__main__':
    start_app()
