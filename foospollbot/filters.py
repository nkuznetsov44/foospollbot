from typing import Optional
from aiogram.dispatcher.filters import Filter
from aiogram.types.message import Message

from models.entities import UserInfo, UserState
from exceptions import TelegramUserDoesNotExist
from storage import Storage


class BaseUserFilter:
    storage = Storage()

    async def get_user_info(self, telegram_user_id: int) -> Optional[UserInfo]:
        try:
            async with self.storage.session() as session:
                return await self.storage.get_user_info(session, telegram_user_id)
        except TelegramUserDoesNotExist:
            return None


class NewUserFilter(Filter, BaseUserFilter):
    key = "user_state"

    async def check(self, message: Message) -> bool:
        if await self.get_user_info(message.from_user.id):
            return False
        return True


class UserStateFilter(Filter, BaseUserFilter):
    key = "user_state"

    def __init__(self, state: UserState) -> None:
        super().__init__()
        self._state = state

    async def check(self, message: Message) -> bool:
        if user_info := await self.get_user_info(message.from_user.id):
            return user_info.state == self._state
        return False
