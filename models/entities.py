from typing import Optional
from datetime import date, datetime
from dataclasses import dataclass
from enum import Enum, unique


@dataclass
class EvksPlayer:
    id: int
    evks_player_id: int
    first_name: str
    last_name: str
    itsf_first_name: Optional[str]
    itsf_last_name: Optional[str]
    itsf_license: Optional[int]
    foreigner: bool
    last_competition_date: date


@unique
class UserState(Enum):
    COLLECTING_FIRST_NAME = 'collecting_first_name'
    COLLECTING_LAST_NAME = 'collecting_last_name'
    COLLECTING_PHONE = 'collecting_phone'
    COLLECTING_RTSF_URL = 'collecting_rtsf_url'
    IN_REVIEW = 'in_review'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    VOTING = 'voting'
    VOTED = 'voted'


@dataclass
class UserInfo:
    id: int
    telegram_user_id: int

    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    rtsf_url: Optional[str]

    evks_player: Optional[EvksPlayer]

    state: UserState

    created: datetime
    updated: Optional[datetime]


@dataclass
class TelegramUser:
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]

    user_info: UserInfo


@dataclass
class VoteOption:
    id: int
    text: str


@dataclass(frozen=True)
class VoteResult:
    id: int
    telegram_user: TelegramUser
    selected_option: VoteOption
    secret_code: str
    created: datetime
