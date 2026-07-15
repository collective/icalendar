import pytest

from icalendar.prop.float import vFloat


def test_zero():
    assert vFloat(0.0).to_ical() == b"0.0"


def test_roundtrip():
    assert vFloat.from_ical(vFloat("42.0").to_ical()) == 42.0
    assert vFloat.from_ical("42.0") == 42.0


def test_error():
    """Error: not an float string"""
    with pytest.raises(ValueError):
        vFloat.from_ical("not a float")


@pytest.mark.parametrize("value", ["nan", "inf", "-inf", "infinity", "1e999"])
def test_reject_non_finite(value):
    """Non-finite floats are not valid FLOAT values per RFC 5545."""
    with pytest.raises(ValueError):
        vFloat.from_ical(value)


def test_ical_value():
    """ical_value property returns the float value."""
    assert vFloat(1.0).ical_value == 1.0
    assert vFloat(0.0).ical_value == 0.0
