from typing import Optional
from uuid import UUID
from datetime import date, datetime
from dataclasses import dataclass, field
from enum import Enum, unique


@dataclass
class EvksPlayer:
    id: int
    first_name: str
    last_name: str
    foreigner: bool
    last_competition_date: date
    itsf_first_name: Optional[str] = None
    itsf_last_name: Optional[str] = None
    itsf_license: Optional[int] = None


@unique
class UserState(Enum):
    COLLECTING_FIRST_NAME = "collecting_first_name"
    COLLECTING_LAST_NAME = "collecting_last_name"
    COLLECTING_PHONE = "collecting_phone"
    COLLECTING_RTSF_URL = "collecting_rtsf_url"
    COLLECTING_PHOTO = "collecting_photo"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    VOTING = "voting"
    VOTED = "voted"


@dataclass
class UserInfo:
    id: int
    telegram_user_id: int
    state: UserState

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    rtsf_url: Optional[str] = None
    evks_player_id: Optional[int] = None
    photo_id: Optional[UUID] = None

    created: Optional[datetime] = field(init=False)
    updated: Optional[datetime] = field(init=False)


@dataclass
class TelegramUser:
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]


@dataclass
class VoteOption:
    id: int
    text: str


@dataclass
class VoteResult:
    id: int
    telegram_user_id: int
    selected_option_id: int
    secret_code: str

    created: Optional[datetime] = field(init=False)
