from dataclasses import dataclass
from importlib.resources import path
from urllib.parse import urlparse
import re
from exceptions import ParseError


class BaseParser:
    def __init__(self, value: str) -> None:
        self._value = value


@dataclass
class RtsfUrlParsingResult:
    url: str
    evks_player_id: int


class RtsfUrlParser(BaseParser):
    """https://rtsf.ru/ratings/player/{evks_player_id}"""

    player_path_re = re.compile(r'(^/ratings/player/)([0-9]+$)')

    def parse(self) -> RtsfUrlParsingResult:
        url = self._value.strip()
        parsed = urlparse(url)

        if parsed.netloc != 'rtsf.ru':
            raise ParseError('Must be rtsf.ru', url)

        path_match = self.player_path_re.match(parsed.path)
        if not path_match:
            raise ParseError('URL path does not match expected regexp', url)

        player_id = int(path_match.groups()[1])
        return RtsfUrlParsingResult(url=url, evks_player_id=player_id)


class PhoneParser(BaseParser):
    def parse(self) -> str:
        # TODO: implement phone validation
        return self._value.strip()
