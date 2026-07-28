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


@pytest.mark.parametrize("attribute", ["REPEAT", "repeat"])
def test_repeat_rejects_negative_values(attribute):
    """REPEAT values must be non-negative according to RFC 5545."""
    alarm = Alarm()
    with pytest.raises(ValueError, match="REPEAT must be >= 0"):
        setattr(alarm, attribute, -1)


@pytest.mark.parametrize("attribute", ["REPEAT", "repeat"])
@pytest.mark.parametrize("value", [0, 1])
def test_repeat_accepts_zero_and_positive_values(attribute, value):
    """Both Alarm REPEAT accessors accept the inclusive lower boundary."""
    alarm = Alarm()
    setattr(alarm, attribute, value)
    assert getattr(alarm, attribute) == value


def test_repeat_rejects_negative_values_added_directly():
    """Invalid parsed REPEAT values raise InvalidCalendar when read."""
    alarm = Alarm({"REPEAT": -1})
    with pytest.raises(InvalidCalendar, match="REPEAT must be >= 0"):
        alarm.repeat  # noqa: B018, RUF100


def test_alarm_to_string():
    a = Alarm()
    a.REPEAT = 11
    assert a.to_ical() == b"BEGIN:VALARM\r\nREPEAT:11\r\nEND:VALARM\r\n"
