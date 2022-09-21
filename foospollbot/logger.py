from typing import Any
from logging import Logger, LoggerAdapter


class ContextLoggerAdapter(LoggerAdapter):
    def __init__(self, logger: Logger) -> None:
        super.__init__(logger, {})
        self._logger = logger
        self._context: dict[str, Any] = {}

    def context_push(self, **kwargs: Any):
        self._context |= kwargs

    def process(self, msg, kwargs):
        extra = kwargs.setdefault("extra", {})
        extra["context"] = self._context
        return msg, kwargs
