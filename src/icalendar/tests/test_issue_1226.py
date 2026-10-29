from icalendar.parser.string import _escape_char


def test__escape_char_accepts_bytes():
    assert _escape_char(b"hello,world;test") == r"hello\,world\;test"
