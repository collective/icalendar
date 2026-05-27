import pytest

from icalendar.parser.string import _escape_char, escape_char


def test__escape_char_accepts_bytes():
    assert _escape_char(b"hello,world;test") == r"hello\,world\;test"


def test_escape_char_accepts_bytes():
    with pytest.warns(
        DeprecationWarning,
        match="escape_char is deprecated and will be removed in icalendar 8",
    ):
        assert escape_char(b"hello,world;test") == r"hello\,world\;test"
