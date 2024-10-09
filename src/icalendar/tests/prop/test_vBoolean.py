import pytest

from icalendar.prop import vBoolean


def test_true():
    assert vBoolean(True).to_ical() == b"TRUE"


def test_false():
    assert vBoolean(0).to_ical() == b"FALSE"


def test_roundtrip():
    assert vBoolean.from_ical(vBoolean(True).to_ical()) == True
    assert vBoolean.from_ical("true") == True


def test_error():
    """Error: key not exists"""
    with pytest.raises(ValueError):
        vBoolean.from_ical("ture")
