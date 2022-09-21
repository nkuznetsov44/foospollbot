from dataclasses import dataclass
from urllib.parse import urlparse
import re
from exceptions import RtsfUrlParseError, PhoneParseError


class BaseParser:
    def __init__(self, value: str) -> None:
        self._value = value


@dataclass
class RtsfUrlParsingResult:
    url: str
    evks_player_id: int


class RtsfUrlParser(BaseParser):
    """https://rtsf.ru/ratings/player/{evks_player_id}"""

    player_path_re = re.compile(r"(^/ratings/player/)([0-9]+$)")

    def parse(self) -> RtsfUrlParsingResult:
        url = self._value.strip()
        parsed = urlparse(url)

        if parsed.netloc != "rtsf.ru":
            raise RtsfUrlParseError("Must be rtsf.ru", url)

        path_match = self.player_path_re.match(parsed.path)
        if not path_match:
            raise RtsfUrlParseError("URL path does not match expected regexp", url)

        player_id = int(path_match.groups()[1])
        return RtsfUrlParsingResult(url=url, evks_player_id=player_id)


class PhoneParser(BaseParser):
    phone_re = re.compile(r"^(\+7|8)\d{10}$")

    def parse(self) -> str:
        phone = (
            self._value.strip()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
        )
        phone_match = self.phone_re.match(phone)
        if not phone_match:
            raise PhoneParseError("Phone does not match expected regexp", phone)

        return self._format_phone(phone_match.group())

    def _format_phone(self, parsed_phone: str) -> str:
        if parsed_phone.startswith("8"):
            phone = parsed_phone[1:]
        else:
            phone = parsed_phone[2:]

        return "+7 ({prefix}) {first}-{second}-{third}".format(
            prefix=phone[:3], first=phone[3:6], second=phone[6:8], third=phone[8:]
        )
