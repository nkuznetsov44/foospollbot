from typing import Optional, Any, ClassVar


class ErrorWithParams(Exception):
    reason: ClassVar[str] = 'UNEXPECTED_ERROR'

    def __init__(self, params: Optional[dict[str, Any]]) -> None:
        super().__init__(self.reason)
        self.params = params or {}


class TelegramUserDoesNotExist(ErrorWithParams):
    reason = 'TELEGRAM_USER_DOES_NOT_EXIST'

    def __init__(self, user_id: int) -> None:
        super().__init__(params=dict(user_id=user_id))
