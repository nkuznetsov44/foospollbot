from typing import Optional
from datetime import date, datetime
from dataclasses import dataclass, field
from enum import Enum, unique


@dataclass
class EvksPlayer:
    id: int
    evks_player_id: int
    first_name: str
    last_name: str
    foreigner: bool
    last_competition_date: date
    itsf_first_name: Optional[str] = None
    itsf_last_name: Optional[str] = None
    itsf_license: Optional[int] = None


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
    state: UserState

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    rtsf_url: Optional[str] = None
    evks_player: Optional[EvksPlayer] = None

    created: Optional[datetime] = field(init=False)
    updated: Optional[datetime] = field(init=False)


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

    created: Optional[datetime] = field(init=False)
