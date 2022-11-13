from typing import Optional, Any
from collections import defaultdict
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import select, func

from models.entities import (
    EvksPlayer,
    TelegramUser,
    UserInfo,
    UserState,
    VoteOption,
    VoteResult,
)
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
            select(TelegramUser).where(TelegramUser.id == telegram_user_id)
        )
        try:
            return result.one()[0]
        except NoResultFound as e:
            raise TelegramUserDoesNotExist(telegram_user_id=telegram_user_id) from e

    async def get_user_info(
        self, session: AsyncSession, telegram_user_id: int, for_update: bool = False
    ) -> UserInfo:
        stmt = select(UserInfo).where(UserInfo.telegram_user_id == telegram_user_id)
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

    async def get_accepted_users(self, session: AsyncSession) -> list[int]:
        result = await session.execute(
            select(UserInfo.telegram_user_id).where(
                UserInfo.state == UserState.ACCEPTED
            )
        )
        return result.scalars().all()

    async def get_vote_options(self, session: AsyncSession) -> list[VoteOption]:
        result = await session.execute(select(VoteOption))
        return result.scalars().all()

    async def get_vote_option(
        self, session: AsyncSession, option_id: int
    ) -> VoteOption:
        result = await session.execute(
            select(VoteOption).where(VoteOption.id == option_id)
        )
        return result.one()[0]

    async def get_info(self, session: AsyncSession) -> dict[str, Any]:
        ret: dict[str, Any] = defaultdict(dict)

        states = await session.execute(
            select(UserInfo.state, func.count(UserInfo.id)).group_by(UserInfo.state)
        )
        for row in states.all():
            ret["states"][row[0]] = row[1]

        vote_results = await session.execute(
            select(VoteOption.text, func.count(VoteResult.id))
            .join(VoteResult, VoteOption.id == VoteResult.selected_option_id)
            .group_by(VoteOption.text)
        )
        for row in vote_results.all():
            ret["results"][row[0]] = row[1]

        return ret
