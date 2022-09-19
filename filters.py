from typing import Optional
from aiogram.dispatcher.filters import Filter
from aiogram.types.message import Message
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import TelegramUser, UserState
from storage import Storage


class UserStateFilter(Filter):
    storage = Storage()

    def __init__(self, state: UserState) -> None:
        super().__init__()
        self._state = state

    async def check(self, message: Message) -> bool:
        async with self.storage.session() as session:
            result = await session.execute(
                select(TelegramUser)
                .options(joinedload(TelegramUser.user_info))
                .where(TelegramUser.id == message.from_user.id)
            )
            telegram_user: Optional[TelegramUser] = result.scalars().first()
            if not telegram_user:
                return False
            return telegram_user.user_info.state == self._state
