"""Test the properties of the alarm."""

from datetime import timedelta

import pytest

from icalendar import ACTION
from icalendar.cal.alarm import Alarm
from icalendar.error import InvalidCalendar


def test_ACTION_absent():
    """An absent ACTION has the documented default."""
    assert Alarm().ACTION == ""


def test_ACTION_enum_values():
    """ACTION exposes the RFC-defined alarm actions as a string enum."""
    assert [action.value for action in ACTION] == ["AUDIO", "DISPLAY", "EMAIL"]
    alarm = Alarm.new_display("Reminder", timedelta(minutes=-5))
    assert alarm.ACTION is ACTION.DISPLAY


def test_ACTION_preserves_extension_values():
    """Unknown IANA and X- actions remain lossless string values."""
    alarm = Alarm()
    alarm.ACTION = "X-CUSTOM"
    assert alarm.ACTION == "X-CUSTOM"
    assert not isinstance(alarm.ACTION, ACTION)
    assert b"ACTION:X-CUSTOM\r\n" in alarm.to_ical()


def test_ACTION_none_deletes_property():
    """Setting ACTION to None removes the property."""
    alarm = Alarm()
    alarm.ACTION = "DISPLAY"

    alarm.ACTION = None

    assert alarm.ACTION == ""
    assert "ACTION" not in alarm


def test_ACTION_uses_first_repeated_property():
    """Reading repeated ACTION properties uses the first value."""
    alarm = Alarm()
    alarm.add("ACTION", "DISPLAY")
    alarm.add("ACTION", "EMAIL")

    assert alarm.ACTION is ACTION.DISPLAY


@pytest.mark.parametrize("action", ["AUDIO", "DISPLAY", "EMAIL"])
def test_ACTION_round_trip(action):
    """Each RFC 5545 ACTION can be read, serialized, and deleted."""
    alarm = Alarm()

    alarm.ACTION = action
    assert alarm.ACTION is ACTION(action)
    assert alarm["ACTION"] == action
    assert f"ACTION:{action}\r\n".encode() in alarm.to_ical()

    del alarm.ACTION
    assert "ACTION" not in alarm


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
    with pytest.raises(TypeError):
        a.REPEAT = "asd"
    a["REPEAT"] = "asd"
    with pytest.raises(InvalidCalendar):
        a.REPEAT  # noqa: B018, RUF100


def test_alarm_to_string():
    a = Alarm()
    a.REPEAT = 11
    assert a.to_ical() == b"BEGIN:VALARM\r\nREPEAT:11\r\nEND:VALARM\r\n"
