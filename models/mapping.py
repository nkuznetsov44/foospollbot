from sqlalchemy.orm import registry, relationship
from models.tables import (
    telegram_users,
    evks_players,
    user_infos,
    vote_options,
    vote_results,
)
from models.entities import (
    TelegramUser,
    EvksPlayer,
    UserInfo,
    VoteOption,
    VoteResult,
)


mapper_registry = registry()

mapper_registry.map_imperatively(
    TelegramUser,
    telegram_users,
    properties={
        'user_info': relationship(UserInfo, uselist=False)
    },
)

mapper_registry.map_imperatively(EvksPlayer, evks_players)

mapper_registry.map_imperatively(
    UserInfo,
    user_infos,
    properties={
        'evks_player': relationship(EvksPlayer, uselist=False)
    }
)

mapper_registry.map_imperatively(VoteOption, vote_options)

mapper_registry.map_imperatively(
    VoteResult,
    vote_results,
    properties={
        'telegram_user': relationship(TelegramUser, uselist=False),
        'vote_option': relationship(VoteOption, uselist=False),
    }
)
