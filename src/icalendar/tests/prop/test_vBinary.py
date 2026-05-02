"""Test vBinary"""

import pytest

from icalendar import vBinary
from icalendar.parser import Parameters


def test_text():
    txt = b"This is gibberish"
    txt_ical = b"VGhpcyBpcyBnaWJiZXJpc2g="
    assert vBinary(txt).to_ical() == txt_ical
    assert vBinary.from_ical(txt_ical) == txt


def test_binary():
    txt = b"Binary data \x13 \x56"
    txt_ical = b"QmluYXJ5IGRhdGEgEyBW"
    assert vBinary(txt).to_ical() == txt_ical
    assert vBinary.from_ical(txt_ical) == txt


def test_param():
    assert isinstance(vBinary("txt").params, Parameters)
    assert vBinary("txt").params == {"VALUE": "BINARY", "ENCODING": "BASE64"}


def test_long_data():
    """Long data should not have line breaks, as that would interfere"""
    txt = b"a" * 99
    txt_ical = b"YWFh" * 33
    assert vBinary(txt).to_ical() == txt_ical
    assert vBinary.from_ical(txt_ical) == txt


def test_repr():
    instance = vBinary("value")
    assert repr(instance) == "vBinary(b'dmFsdWU=')"


def test_from_ical():
    with pytest.raises(ValueError, match=r"Not valid base 64 encoding\."):
        vBinary.from_ical("value")
    with pytest.raises(ValueError, match=r"Not valid base 64 encoding\."):
        vBinary.from_ical("áèਮ")


@pytest.mark.parametrize(
    "value",
    [
        "!!!!dGV4dA==@@@@",
        "dG V4dA==",
        "dGV4dA==#",
    ],
)
def test_from_ical_rejects_non_base64_characters(value):
    with pytest.raises(ValueError, match=r"Not valid base 64 encoding\."):
        vBinary.from_ical(value)


def test_ical_value():
    """ical_value property returns the bytes value."""
    data = b"magic string"
    assert vBinary(data).ical_value == data


def test_ical_value_with_string():
    """ical_value property still decodes strings for backward compatibility."""
    b64_str = "SGVsbG8="
    assert vBinary(b64_str).ical_value == b"Hello"


def test_hash():
    obj = vBinary(b"hashed text")
    assert hash(obj) == hash(b"hashed text")
