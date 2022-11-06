from typing import Any
import logging
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from log4mongo.handlers import MongoHandler
from settings import settings


LOGGER_NAME = "app"


class ContextLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__(logger, {})
        self._logger = logger
        self._context_stack: list[dict[str, Any]] = [{}]

    def _get_context(self) -> dict[str, Any]:
        return self._context_stack[-1]

    def context_push(self, **kwargs: Any):
        context = self._get_context()
        context |= kwargs

    def process(self, msg, kwargs):  # type: ignore
        extra = kwargs.setdefault("extra", {})
        extra["context"] = self._get_context()
        return msg, kwargs

    def __enter__(self) -> None:
        new_context = {**self._get_context()}
        self._context_stack.append(new_context)

    def __exit__(self, exc_type, exc_value, traceback):  # type: ignore
        self._context_stack.pop()


def setup_logger():
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s - %(context)s"
    )
    stream_handler.setFormatter(formatter)

    mongo_handler = MongoHandler(
        host=settings["mongo_logs"]["host"],
        port=settings["mongo_logs"]["port"],
    )

    level = logging.getLevelName(settings["log_level"])
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.addHandler(stream_handler)
    logger.addHandler(mongo_handler)


def get_logger() -> ContextLoggerAdapter:
    _logger = logging.getLogger(LOGGER_NAME)
    return ContextLoggerAdapter(_logger)


class LoggingMiddlewareAdapter(LoggingMiddleware):
    def __init__(self, logger: ContextLoggerAdapter) -> None:
        super().__init__()
        self.logger = logger
