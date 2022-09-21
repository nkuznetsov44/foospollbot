import pytest
from parsers import PhoneParser, RtsfUrlParser
from exceptions import PhoneParseError, RtsfUrlParseError


class TestPhoneParser:
    @pytest.mark.parametrize(
        "phone",
        (
            "+79999999999",
            "+7 999 999 99 99",
            "+7 (999) 999 99 99",
            "+7 (999) 999-99-99",
            "+7(999)999-99-99",
            "+7-999-999-99-99",
            "+7 999 999-99-99",
            "89999999999",
            "8 999 999 99 99",
            "8 (999) 999 99 99",
            "8 (999) 999-99-99",
            "8(999)999-99-99",
            "8-999-999-99-99",
            "8 999 999-99-99",
        ),
    )
    def test_success(self, phone):
        expected_result = "+7 (999) 999-99-99"
        result = PhoneParser(phone).parse()
        assert result == expected_result

    @pytest.mark.parametrize(
        "phone",
        (
            "" "+44 999 999 99 99",
            "123",
            "+7 +7 4444 99 99",
        ),
    )
    def test_error(self, phone):
        with pytest.raises(PhoneParseError):
            PhoneParser(phone).parse()


class TestRtsfUrlParser:
    @pytest.mark.parametrize(
        "url,expected_player_id",
        (
            ("https://rtsf.ru/ratings/player/1", 1),
            ("https://rtsf.ru/ratings/player/111", 111),
        ),
    )
    def test_success(self, url, expected_player_id):
        result = RtsfUrlParser(url).parse()
        assert result.evks_player_id == expected_player_id

    @pytest.mark.parametrize(
        "url",
        (
            "rtsf.ru/ratings/player/1",
            "https://rtsf.ru/ratings/player/",
            "https://rtsf.ru/ratings/player/xxx",
            "https://yandex.ru/ratings/player/1",
        ),
    )
    def test_error(self, url):
        with pytest.raises(RtsfUrlParseError):
            RtsfUrlParser(url).parse()
