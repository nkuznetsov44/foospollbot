from aiogram.dispatcher import Dispatcher
from aiogram.bot import Bot
from aiogram.utils.executor import start_webhook
from sqlalchemy.ext.asyncio import create_async_engine
from settings import settings
from storage import Storage
from models.mapping import mapper_registry
from logger import get_logger, setup_logger, LoggingMiddlewareAdapter


bot = Bot(token=settings["telegram_token"])
dp = Dispatcher(bot)
setup_logger()
logger = get_logger()
dp.middleware.setup(LoggingMiddlewareAdapter(logger=logger))

connection_string = (
    "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
        **settings["db"]
    )
)
engine = create_async_engine(connection_string)
mapper_registry.configure()
storage = Storage()
storage.setup_db_engine(engine)


async def on_startup(_: Dispatcher) -> None:
    await bot.set_webhook(settings["webhook_url"])


async def on_shutdown(_: Dispatcher) -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.delete_webhook(settings["webhook_url"])


def start_app() -> None:
    start_webhook(
        dispatcher=dp,
        webhook_path=settings["webhook_path"],
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=settings["host"],
        port=settings["port"],
        skip_updates=True,
    )
