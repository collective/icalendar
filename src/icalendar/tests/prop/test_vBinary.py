"""Test vBinary"""

import base64

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


def test_ical_value():
    """ical_value property returns the string value."""
    magic_string = base64.b64encode(b"magic string")
    assert vBinary(magic_string).ical_value == base64.b64decode(magic_string)


def test_hash():
    obj = vBinary(b"hashed text")
    assert hash(obj) == hash(b"hashed text")
