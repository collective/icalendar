"""Test the alarm time computation."""

from datetime import datetime, timedelta, timezone

import pytest

from icalendar.alarms import Alarms
from icalendar.cal import Alarm, InvalidCalendar
from icalendar.prop import vDatetime

EXAMPLE_TRIGGER = datetime(1997, 3, 17, 13, 30, tzinfo=timezone.utc)


def test_absolute_alarm_time_rfc_example(alarms):
    """Check that the absolute alarm is recognized.

    The following example is for a "VALARM" calendar component
    that specifies an audio alarm that will sound at a precise time
    and repeat 4 more times at 15-minute intervals:
    """
    a = Alarms(alarms.rfc_5545_absolute_alarm_example)
    times = a.times
    assert len(times) == 5
    for i, t in enumerate(times):
        assert t.trigger == EXAMPLE_TRIGGER + timedelta(minutes=15 * i)


alarm_1 = Alarm()
alarm_1.add("TRIGGER", EXAMPLE_TRIGGER)
alarm_2 = Alarm()
alarm_2["TRIGGER"] = vDatetime(EXAMPLE_TRIGGER)

@pytest.mark.parametrize(
    "alarm",
    [
        alarm_1, alarm_2
    ]
)
def test_absolute_alarm_time_with_vDatetime(alarm):
    """Check that the absolute alarm is recognized.

    The following example is for a "VALARM" calendar component
    that specifies an audio alarm that will sound at a precise time
    and repeat 4 more times at 15-minute intervals:
    """
    a = Alarms(alarm)
    times = a.times
    assert len(times) == 1
    assert times[0].trigger == EXAMPLE_TRIGGER



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
        a.REPEAT  # noqa: B018


def test_alarm_to_string():
    a = Alarm()
    a.REPEAT = 11
    assert a.to_ical() == b"BEGIN:VALARM\r\nREPEAT:11\r\nEND:VALARM\r\n"


def test_alarm_has_only_one_of_repeat_or_duration():
    """This is an edge case and we should ignore the repetition."""
    pytest.skip("TODO")
