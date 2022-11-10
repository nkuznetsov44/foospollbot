from typing import ClassVar, Sequence
from dataclasses import dataclass
import asyncio
from aiogram.bot import Bot
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models.entities import VoteOption
from state_machine import UserStateMachine
from storage import Storage
from logger import get_logger


@dataclass(frozen=True)
class Poll:
    telegram_user_id: int
    options: tuple[VoteOption]


VoteOptionCallback = CallbackData("VOTE_OPTION", "option_id")


class AbstractPollSender:
    bot: ClassVar[Bot]
    storage: ClassVar[Storage]
    logger = get_logger()

    CONCURRENT_POLLS = 3

    def __init__(self, user_ids: Sequence[int], options: tuple[VoteOption]) -> None:
        self.polls = tuple(
            Poll(telegram_user_id=uid, options=options) for uid in user_ids
        )
        self._sem = asyncio.Semaphore(self.CONCURRENT_POLLS)

    async def _send_poll(self, poll: Poll) -> None:
        async with self._sem:
            with self.logger:
                self.logger.context_push(telegram_user_id=poll.telegram_user_id)
                self.logger.info("SENDING_POLL")

                try:
                    inline_keyboard: list[list[InlineKeyboardButton]] = []
                    for option in poll.options:
                        inline_keyboard.append(
                            [
                                InlineKeyboardButton(
                                    text=option.text,
                                    callback_data=VoteOptionCallback.new(
                                        option_id=option.id
                                    ),
                                )
                            ]
                        )
                    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

                    async with self.storage.session() as session:
                        user_info = await self.storage.get_user_info(
                            session=session,
                            telegram_user_id=poll.telegram_user_id,
                            for_update=True,
                        )
                        user_sm = UserStateMachine(user_info.state)
                        user_sm.start_vote(user_info)
                        user_info.state = user_sm.state
                        session.add(user_info)
                        await session.commit()

                    self.logger.info("UPDATED_USER_STATE")

                    await self.bot.send_message(
                        chat_id=poll.telegram_user_id,
                        text=(
                            "Пришло время проголосовать. К этому сообщению "
                            "прикреплены кнопки с именами кандидатов. "
                            "Внимательно и аккуратно нажмите на кандидата, "
                            "за которого вы хотите отдать свой голос. "
                            "Возможности переголосовать не будет."
                        ),
                        reply_markup=keyboard,
                    )

                    self.logger.info("FINISH_SENDING_POLL")
                except:  # noqa: E722
                    self.logger.exception("SENDING_POLL_FAILED")
                    raise

                await asyncio.sleep(2)  # sleep 2 seconds after completing poll sending

    async def send(self) -> None:
        tasks = [asyncio.ensure_future(self._send_poll(poll)) for poll in self.polls]
        self.logger.info("STARTING_POLLS_SENDING_PROCESS")
        await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info("FINISHED_POLLS_SENDING_PROCESS")
