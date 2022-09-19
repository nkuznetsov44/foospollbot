import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.bot import Bot
from aiogram.utils.executor import start_webhook
from sqlalchemy.ext.asyncio import create_async_engine
from settings import settings
from storage import Storage


level = logging.getLevelName(settings['log_level'])
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)

bot = Bot(token=settings['telegram_token'])
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

connection_string = (
    "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
        **settings['db']
    )
)
engine = create_async_engine(connection_string, echo=True)
storage = Storage()
storage.setup_db_engine(engine)


async def on_startup(_: Dispatcher) -> None:
    await bot.set_webhook(settings['webhook_url'])


async def on_shutdown(_: Dispatcher) -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()
    await bot.delete_webhook(settings['webhook_url'])


def start_app() -> None:
    start_webhook(
        dispatcher=dp,
        webhook_path=settings['webhook_path'],
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=settings['host'],
        port=settings['port'],
        skip_updates=True
    )
