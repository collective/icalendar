"""Test the properties of the alarm."""

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.error import InvalidCalendar


def test_repeat_absent():
    """Test the absence of REPEAT."""
    assert Alarm().REPEAT == 0


def test_repeat_number():
    """Test the absence of REPEAT."""
    assert Alarm({"REPEAT": 10}).REPEAT == 10


def test_set_REPEAT():
    """Check setting the value."""
    a = Alarm()
    a.REPEAT = 10
    assert a.REPEAT == 10


def test_set_REPEAT_twice():
    """Check setting the value."""
    a = Alarm()
    a.REPEAT = 10
    a.REPEAT = 20
    assert a.REPEAT == 20


def test_add_REPEAT():
    """Check setting the value."""
    a = Alarm()
    a.add("REPEAT", 10)
    assert a.REPEAT == 10


def test_invalid_repeat_value():
    """Check setting the value."""
    a = Alarm()
    with pytest.raises(ValueError):
        a.REPEAT = "asd"
    a["REPEAT"] = "asd"
    with pytest.raises(InvalidCalendar):
        a.REPEAT  # noqa: B018, RUF100


def test_alarm_to_string():
    a = Alarm()
    a.REPEAT = 11
    assert a.to_ical() == b"BEGIN:VALARM\r\nREPEAT:11\r\nEND:VALARM\r\n"


def test_set_REPEAT_to_zero():
    """Zero is the boundary and a valid value."""
    a = Alarm()
    a.REPEAT = 0
    assert a.REPEAT == 0


@pytest.mark.parametrize("value", [-1, -10])
def test_set_negative_REPEAT(value):
    """Setting a negative REPEAT raises a ValueError."""
    a = Alarm()
    with pytest.raises(ValueError, match="REPEAT must be an int >= 0"):
        a.REPEAT = value


@pytest.mark.parametrize("value", [-1, -10])
def test_set_negative_repeat_lowercase(value):
    """The lowercase repeat property validates the same way."""
    a = Alarm()
    with pytest.raises(ValueError, match="REPEAT must be an int >= 0"):
        a.repeat = value


def test_negative_repeat_keeps_existing_value():
    """A failed set does not modify the existing value."""
    a = Alarm()
    a.REPEAT = 3
    with pytest.raises(ValueError):
        a.REPEAT = -1
    assert a.REPEAT == 3
