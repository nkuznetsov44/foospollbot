from typing import Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import select

from models.entities import EvksPlayer, TelegramUser, UserInfo
from exceptions import EvksPlayerDoesNotExist, TelegramUserDoesNotExist


class Storage:
    db_engine: Optional[AsyncEngine] = None

    @classmethod
    def setup_db_engine(cls, db_engine: AsyncEngine) -> None:
        cls.db_engine = db_engine

    def _sessionmaker(self):
        return sessionmaker(self.db_engine, expire_on_commit=False, class_=AsyncSession)

    @asynccontextmanager
    async def session(self) -> AsyncSession:
        async with self._sessionmaker()() as session:
            yield session

    async def get_telegram_user(
        self, session: AsyncSession, telegram_user_id: int
    ) -> TelegramUser:
        result = await session.execute(
            select(TelegramUser)
            .where(TelegramUser.id == telegram_user_id)
        )
        try:
            return result.one()[0]
        except NoResultFound as e:
            raise TelegramUserDoesNotExist(telegram_user_id=telegram_user_id) from e

    async def get_user_info(
        self, session: AsyncSession, telegram_user_id: int, for_update: bool = False
    ) -> UserInfo:
        stmt = (
            select(UserInfo)
            .where(UserInfo.telegram_user_id == telegram_user_id)
        )
        if for_update:
            stmt = stmt.with_for_update()

        result = await session.execute(statement=stmt)
        try:
            return result.one()[0]
        except NoResultFound as e:
            raise TelegramUserDoesNotExist(telegram_user_id=telegram_user_id) from e

    async def get_evks_player(
        self, session: AsyncSession, evks_player_id: int
    ) -> EvksPlayer:
        result = await session.execute(
            select(EvksPlayer).where(EvksPlayer.id == evks_player_id)
        )
        try:
            return result.one()[0]
        except NoResultFound as e:
            raise EvksPlayerDoesNotExist(evks_player_id=evks_player_id) from e
