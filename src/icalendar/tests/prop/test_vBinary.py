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
    """ical_value property returns the binary value."""
    raw_data = b"magic string"
    assert vBinary(raw_data).ical_value == raw_data


def test_ical_value_returns_raw_bytes_not_decoded():
    """ical_value returns the raw stored bytes; it does not base64-decode them.

    This is the breaking change from #1356. Previously ical_value decoded the
    stored value as base64 (so ``vBinary("SGVsbG8=").ical_value`` was ``b"Hello"``)
    and raised ValueError for non-base64 input. See news/1356.breaking.
    """
    assert vBinary(b"SGVsbG8=").ical_value == b"SGVsbG8="
    # Non-base64 input no longer raises; it is just stored and returned as-is.
    assert vBinary(b"!!!!dGV4dA==@@@@").ical_value == b"!!!!dGV4dA==@@@@"


def test_bytes_holds_raw_lossless_data():
    """The .bytes attribute exposes the raw value, including non-UTF-8 data."""
    raw = bytes(range(256))
    binary = vBinary(raw)
    assert binary.bytes == raw
    # round-trips losslessly through the wire format
    assert vBinary.from_ical(binary.to_ical()) == raw


def test_obj_is_deprecated_string_view():
    """.obj is kept for backward compatibility but deprecated in favour of .bytes."""
    with pytest.warns(DeprecationWarning, match="obj is deprecated"):
        assert vBinary(b"txt").obj == "txt"


def test_obj_setter_updates_bytes():
    """Setting .obj still works for backward compatibility and writes .bytes."""
    binary = vBinary(b"old")
    with pytest.warns(DeprecationWarning, match="obj is deprecated"):
        binary.obj = "new"
    assert binary.bytes == b"new"


def test_hash():
    obj = vBinary(b"hashed text")
    assert hash(obj) == hash(b"hashed text")
