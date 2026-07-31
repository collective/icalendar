"""Test the properties of the alarm."""

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.error import InvalidCalendar


def test_ACTION_absent():
    """An absent ACTION has the documented default."""
    assert Alarm().ACTION == ""


@pytest.mark.parametrize("action", ["AUDIO", "DISPLAY", "EMAIL"])
def test_ACTION_round_trip(action):
    """Each RFC 5545 ACTION can be read, serialized, and deleted."""
    alarm = Alarm()

    alarm.ACTION = action
    assert alarm.ACTION == action
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
    with pytest.raises(ValueError):
        a.REPEAT = "asd"
    a["REPEAT"] = "asd"
    with pytest.raises(InvalidCalendar):
        a.REPEAT  # noqa: B018, RUF100


def test_alarm_to_string():
    a = Alarm()
    a.REPEAT = 11
    assert a.to_ical() == b"BEGIN:VALARM\r\nREPEAT:11\r\nEND:VALARM\r\n"


def test_attachments_empty():
    a = Alarm()
    assert a.attachments == []


def test_attachments_setter_uri():
    a = Alarm()
    a.attachments = "ftp://example.com/bell.aud"
    assert len(a.attachments) == 1
    assert str(a.attachments[0]) == "ftp://example.com/bell.aud"


def test_attachments_setter_binary():
    a = Alarm()
    a.attachments = b"\x00\x01raw"
    assert len(a.attachments) == 1


def test_attachments_setter_list():
    a = Alarm()
    a.attachments = ["ftp://example.com/a.aud", b"\x00\x01"]
    assert len(a.attachments) == 2


def test_attachments_setter_replaces():
    a = Alarm()
    a.attachments = "ftp://example.com/old.aud"
    a.attachments = "ftp://example.com/new.aud"
    assert len(a.attachments) == 1
    assert str(a.attachments[0]) == "ftp://example.com/new.aud"


def test_attachments_setter_none_clears():
    a = Alarm()
    a.attachments = "ftp://example.com/bell.aud"
    a.attachments = None
    assert a.attachments == []


def test_attachments_deleter():
    a = Alarm()
    a.attachments = "ftp://example.com/bell.aud"
    del a.attachments
    assert a.attachments == []


def test_attachments_returns_copy():
    a = Alarm()
    a.attachments = "ftp://example.com/bell.aud"
    lst = a.attachments
    lst.append("extra")
    assert len(a.attachments) == 1
