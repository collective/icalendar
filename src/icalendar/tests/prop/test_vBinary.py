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
    """Test that ``ical_value`` returns the raw stored bytes.

    With the release of icalendar 7.1.0, and previous to PR #1356,
    ``ical_value`` Base64-decoded the raw stored bytes. For example,
    ``vBinary("SGVsbG8=").ical_value`` was decoded to ``b"Hello"``
    and raised ``ValueError`` for non-Base64 input.
    """
    assert vBinary(b"SGVsbG8=").ical_value == b"SGVsbG8="
    # Non-base64 input no longer raises; it is just stored and returned as-is.
    assert vBinary(b"!!!!dGV4dA==@@@@").ical_value == b"!!!!dGV4dA==@@@@"


def test_bytes_holds_raw_lossless_data():
    """The .bytes attribute exposes the raw value, including non-UTF-8 data.

    See PR #1356.
    """
    raw = bytes(range(256))
    binary = vBinary(raw)
    assert binary.bytes == raw
    # round-trips losslessly through the wire format
    assert vBinary.from_ical(binary.to_ical()) == raw


def test_obj_is_deprecated_string_view():
    """.obj is kept for backward compatibility but deprecated in favour of .bytes.

    See PR #1356.
    """
    with pytest.warns(DeprecationWarning, match="obj is deprecated"):
        assert vBinary(b"txt").obj == "txt"


def test_obj_setter_updates_bytes():
    """Setting .obj still works for backward compatibility and writes .bytes.

    See PR #1356.
    """
    binary = vBinary(b"old")
    with pytest.warns(DeprecationWarning, match="obj is deprecated"):
        binary.obj = "new"
    assert binary.bytes == b"new"


def test_hash():
    obj = vBinary(b"hashed text")
    assert hash(obj) == hash(b"hashed text")


def test_base64data_getter():
    """base64data returns the same string as to_ical(), decoded to str."""
    obj = vBinary(b"This is gibberish")
    assert obj.base64data == "VGhpcyBpcyBnaWJiZXJpc2g="
    assert obj.base64data == obj.to_ical().decode("ascii")


def test_base64data_getter_empty():
    """base64data of an empty value is an empty string."""
    assert vBinary(b"").base64data == ""


def test_base64data_setter():
    """Setting base64data updates the underlying value."""
    obj = vBinary(b"initial value")
    obj.base64data = "QmluYXJ5IGRhdGEgEyBW"
    assert obj.to_ical() == b"QmluYXJ5IGRhdGEgEyBW"
    assert obj.from_ical(obj.to_ical()) == b"Binary data \x13 \x56"


def test_base64data_roundtrip():
    """Reading base64data after setting it returns the same string."""
    obj = vBinary(b"initial value")
    obj.base64data = "QmluYXJ5IGRhdGEgEyBW"
    assert obj.base64data == "QmluYXJ5IGRhdGEgEyBW"


@pytest.mark.parametrize(
    "value",
    [
        "value",
        "áèਮ",
        "!!!!dGV4dA==@@@@",
        "dG V4dA==",
        "dGV4dA==#",
    ],
)
def test_base64data_setter_rejects_invalid_base64(value):
    """The setter raises ValueError, matching from_ical's error, for bad input."""
    obj = vBinary(b"unchanged")
    with pytest.raises(ValueError, match=r"Not valid base 64 encoding\."):
        obj.base64data = value
    # a rejected assignment must not mutate the existing value
    assert obj.to_ical() == vBinary(b"unchanged").to_ical()


def test_base64data_setter_rejects_non_str():
    """Non-str input raises TypeError, matching base64.b64decode's behaviour."""
    obj = vBinary(b"unchanged")
    with pytest.raises(TypeError):
        obj.base64data = 12345


def test_base64data_setter_stores_raw_bytes():
    """The setter writes the decoded bytes to .bytes, so non-UTF-8 data round-trips.

    See PR #1356.
    """
    raw = bytes(range(256))
    encoded = base64.b64encode(raw).decode("ascii")
    obj = vBinary(b"")
    obj.base64data = encoded
    assert obj.bytes == raw
    assert obj.base64data == encoded


def test_attach_example_preserves_binary_data(calendars):
    """The example calendar's PNG attachment round-trips without corruption.

    Regression test for the corruption fixed in #1356. See #1549.
    """
    calendar = calendars.issue_1549_binary_attachment
    event = calendar.subcomponents[0]
    attach = event["ATTACH"]

    assert attach.bytes[:6] == b"\x89PNG\r\n"
