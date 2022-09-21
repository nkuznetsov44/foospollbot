from typing import Optional, Any, ClassVar


class ErrorWithParams(Exception):
    reason: ClassVar[str] = "UNEXPECTED_ERROR"

    def __init__(
        self, message: Optional[str] = None, params: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message or self.reason)
        self.params = params or {}


class TelegramUserDoesNotExist(ErrorWithParams):
    reason = "TELEGRAM_USER_DOES_NOT_EXIST"

    def __init__(self, telegram_user_id: int) -> None:
        super().__init__(params=dict(telegram_user_id=telegram_user_id))


class EvksPlayerDoesNotExist(ErrorWithParams):
    reason = "EVKS_PLAYER_DOES_NOT_EXIST"

    def __init__(self, evks_player_id: int) -> None:
        super().__init__(params=dict(evks_player_id=evks_player_id))


class EvksPlayerAlreadyRegistered(ErrorWithParams):
    reason = "EVKS_PLAYER_ALREADY_REGISTERED"

    def __init__(self, evks_player_id: int) -> None:
        super().__init__(params=dict(evks_player_id=evks_player_id))


class ParseError(ErrorWithParams):
    reason = "PARSE_ERROR"

    def __init__(self, message: str, value: Any) -> None:
        super().__init__(message=message, params=dict(value=value))


class PhoneParseError(ParseError):
    reason = "PHONE_PARSE_ERROR"


class RtsfUrlParseError(ParseError):
    reason = "EVKS_URL_PARSE_ERROR"
