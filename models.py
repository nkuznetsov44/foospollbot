from enum import Enum, unique

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


Base = declarative_base()


class TelegramUser(Base):
    __tablename__ = 'telegram_users'
    id = sa.Column(sa.Integer, primary_key=True)
    telegram_user_id = sa.Column(sa.Integer, unique=True)
    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    username = sa.Column(sa.String, nullable=True)

    user_info = relationship('UserInfo', uselist=False)


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


class UserInfo(Base):
    __tablename__ = 'user_infos'
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(TelegramUser.id))

    first_name = sa.Column(sa.String, nullable=True)
    last_name = sa.Column(sa.String, nullable=True)
    phone = sa.Column(sa.String, nullable=True)
    rtsf_url = sa.Column(sa.String, nullable=True)

    state = sa.Column(sa.Enum(UserState))

    created = sa.Column(sa.DateTime, server_default=func.now())
    updated = sa.Column(sa.DateTime, onupdate=func.now())


class VoteOption(Base):
    __tablename__ = 'vote_options'
    id = sa.Column(sa.Integer, primary_key=True)
    text = sa.Column(sa.Text)


class VoteResult(Base):
    __tablename__ = 'vote_results'
    __table_args__ = (
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('secret_code'),
    )
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(TelegramUser.id))
    selected_option_id = sa.Column(sa.Integer, sa.ForeignKey(VoteOption.id))
    secret_code = sa.Column(sa.String)
