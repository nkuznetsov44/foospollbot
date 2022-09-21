import sqlalchemy as sa
from sqlalchemy.sql import func
from models.entities import UserState


metadata_obj = sa.MetaData()

telegram_users = sa.Table(
    "telegram_users",
    metadata_obj,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("first_name", sa.String, nullable=True),
    sa.Column("last_name", sa.String, nullable=True),
    sa.Column("username", sa.String, nullable=True),
)

evks_players = sa.Table(
    "evks_players",
    metadata_obj,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("first_name", sa.String),
    sa.Column("last_name", sa.String),
    sa.Column("itsf_first_name", sa.String, nullable=True),
    sa.Column("itsf_last_name", sa.String, nullable=True),
    sa.Column("itsf_license", sa.Integer, nullable=True),
    sa.Column("foreigner", sa.Boolean),
    sa.Column("last_competition_date", sa.Date),
)

user_infos = sa.Table(
    "user_infos",
    metadata_obj,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "telegram_user_id",
        sa.Integer,
        sa.ForeignKey("telegram_users.id", ondelete="CASCADE"),
        unique=True,
    ),
    sa.Column("first_name", sa.String, nullable=True),
    sa.Column("last_name", sa.String, nullable=True),
    sa.Column("phone", sa.String, nullable=True),
    sa.Column("rtsf_url", sa.String, nullable=True),
    sa.Column(
        "evks_player_id", sa.Integer, sa.ForeignKey("evks_players.id"), unique=True
    ),
    sa.Column("state", sa.Enum(UserState)),
    sa.Column("created", sa.DateTime, server_default=func.now()),
    sa.Column("updated", sa.DateTime, onupdate=func.now()),
)

vote_options = sa.Table(
    "vote_options",
    metadata_obj,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("text", sa.Text, unique=True),
)

vote_results = sa.Table(
    "vote_results",
    metadata_obj,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column(
        "telegram_user_id", sa.Integer, sa.ForeignKey("telegram_users.id"), unique=True
    ),
    sa.Column("selected_option_id", sa.Integer, sa.ForeignKey("vote_options.id")),
    sa.Column("secret_code", sa.String, unique=True),
    sa.Column("created", sa.DateTime, server_default=func.now()),
)
