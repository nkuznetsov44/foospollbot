from sqlalchemy.orm import registry
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

mapper_registry.map_imperatively(TelegramUser, telegram_users)

mapper_registry.map_imperatively(EvksPlayer, evks_players)

mapper_registry.map_imperatively(UserInfo, user_infos)

mapper_registry.map_imperatively(VoteOption, vote_options)

mapper_registry.map_imperatively(VoteResult, vote_results)
