from typing import Optional
from aiogram.dispatcher.filters import Filter
from aiogram.types.message import Message
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models.entities import TelegramUser, UserState
from storage import Storage


class BaseUserFilter:
    storage = Storage()

    async def get_user_with_info(self, telegram_user_id: int) -> Optional[TelegramUser]:
        async with self.storage.session() as session:
            result = await session.execute(
                select(TelegramUser)
                .options(joinedload(TelegramUser.user_info))
                .where(TelegramUser.id == telegram_user_id)
            )
            return result.scalars().first()


class NewUserFilter(Filter, BaseUserFilter):
    key = "user_state"

    async def check(self, message: Message) -> bool:
        if await self.get_user_with_info(message.from_user.id):
            return False
        return True


class UserStateFilter(Filter, BaseUserFilter):
    key = "user_state"

    def __init__(self, state: UserState) -> None:
        super().__init__()
        self._state = state

    async def check(self, message: Message) -> bool:
        if user := await self.get_user_with_info(message.from_user.id):
            return user.user_info.state == self._state
        return False
