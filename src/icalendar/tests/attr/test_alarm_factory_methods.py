"""Tests for Alarm.new_display(), Alarm.new_audio(), and Alarm.new_email()."""

from datetime import datetime, timedelta, timezone

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.error import InvalidCalendar
from icalendar.prop import vCalAddress

# ---------------------------------------------------------------------------
# new_display
# ---------------------------------------------------------------------------


def test_new_display_sets_action():
    alarm = Alarm.new_display("Reminder", timedelta(minutes=-15))
    assert alarm["ACTION"] == "DISPLAY"


def test_new_display_sets_description():
    alarm = Alarm.new_display("Stand-up in 15 min", timedelta(minutes=-15))
    assert alarm.description == "Stand-up in 15 min"


def test_new_display_sets_relative_trigger():
    trigger = timedelta(minutes=-30)
    alarm = Alarm.new_display("desc", trigger)
    assert alarm.TRIGGER == trigger


def test_new_display_sets_absolute_trigger():
    trigger = datetime(2025, 1, 1, 9, 0, tzinfo=timezone.utc)
    alarm = Alarm.new_display("desc", trigger)
    assert alarm.TRIGGER == trigger


def test_new_display_with_repeat():
    alarm = Alarm.new_display(
        "desc", timedelta(minutes=-10), duration=timedelta(minutes=5), repeat=2
    )
    assert alarm.DURATION == timedelta(minutes=5)
    assert alarm.REPEAT == 2


def test_new_display_requires_description():
    with pytest.raises(InvalidCalendar, match="description"):
        Alarm.new_display("", timedelta(minutes=-5))


def test_new_display_requires_trigger():
    with pytest.raises(InvalidCalendar, match="trigger"):
        Alarm.new_display("desc", None)


def test_new_display_duration_without_repeat_raises():
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        Alarm.new_display("desc", timedelta(minutes=-5), duration=timedelta(minutes=1))


def test_new_display_repeat_without_duration_raises():
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        Alarm.new_display("desc", timedelta(minutes=-5), repeat=3)


# ---------------------------------------------------------------------------
# new_audio
# ---------------------------------------------------------------------------


def test_new_audio_sets_action():
    alarm = Alarm.new_audio(timedelta(minutes=-5))
    assert alarm["ACTION"] == "AUDIO"


def test_new_audio_sets_trigger():
    trigger = timedelta(minutes=-5)
    alarm = Alarm.new_audio(trigger)
    assert alarm.TRIGGER == trigger


def test_new_audio_without_attach():
    alarm = Alarm.new_audio(timedelta(minutes=-5))
    assert alarm.get("ATTACH") is None


def test_new_audio_with_attach():
    uri = "ftp://example.com/pub/sounds/bell-01.aud"
    alarm = Alarm.new_audio(timedelta(minutes=-5), attach=uri)
    assert str(alarm["ATTACH"]) == uri


def test_new_audio_with_repeat():
    alarm = Alarm.new_audio(
        timedelta(minutes=-5), duration=timedelta(minutes=2), repeat=3
    )
    assert alarm.DURATION == timedelta(minutes=2)
    assert alarm.REPEAT == 3


def test_new_audio_requires_trigger():
    with pytest.raises(InvalidCalendar, match="trigger"):
        Alarm.new_audio(None)


def test_new_audio_duration_without_repeat_raises():
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        Alarm.new_audio(timedelta(minutes=-5), duration=timedelta(minutes=1))


def test_new_audio_repeat_without_duration_raises():
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        Alarm.new_audio(timedelta(minutes=-5), repeat=3)


# ---------------------------------------------------------------------------
# new_email
# ---------------------------------------------------------------------------


def test_new_email_sets_action():
    alarm = Alarm.new_email(
        summary="Reminder",
        description="Your meeting starts soon.",
        trigger=timedelta(minutes=-30),
        attendees=[vCalAddress("mailto:user@example.com")],
    )
    assert alarm["ACTION"] == "EMAIL"


def test_new_email_sets_summary_and_description():
    alarm = Alarm.new_email(
        summary="Subject",
        description="Body",
        trigger=timedelta(minutes=-30),
        attendees=[vCalAddress("mailto:user@example.com")],
    )
    assert alarm.summary == "Subject"
    assert alarm.description == "Body"


def test_new_email_sets_attendees():
    attendees = [
        vCalAddress("mailto:a@example.com"),
        vCalAddress("mailto:b@example.com"),
    ]
    alarm = Alarm.new_email(
        summary="S",
        description="D",
        trigger=timedelta(minutes=-30),
        attendees=attendees,
    )
    assert len(alarm.attendees) == 2


def test_new_email_with_attachment():
    alarm = Alarm.new_email(
        summary="S",
        description="D",
        trigger=timedelta(minutes=-30),
        attendees=[vCalAddress("mailto:user@example.com")],
        attachments=["https://example.com/file.pdf"],
    )
    assert "ATTACH" in alarm


def test_new_email_requires_summary():
    with pytest.raises(InvalidCalendar, match="summary"):
        Alarm.new_email(
            summary="",
            description="D",
            trigger=timedelta(minutes=-30),
            attendees=[vCalAddress("mailto:user@example.com")],
        )


def test_new_email_requires_description():
    with pytest.raises(InvalidCalendar, match="description"):
        Alarm.new_email(
            summary="S",
            description="",
            trigger=timedelta(minutes=-30),
            attendees=[vCalAddress("mailto:user@example.com")],
        )


def test_new_email_requires_trigger():
    with pytest.raises(InvalidCalendar, match="trigger"):
        Alarm.new_email(
            summary="S",
            description="D",
            trigger=None,
            attendees=[vCalAddress("mailto:user@example.com")],
        )


def test_new_email_requires_attendees():
    with pytest.raises(InvalidCalendar, match="attendee"):
        Alarm.new_email(
            summary="S",
            description="D",
            trigger=timedelta(minutes=-30),
            attendees=[],
        )


def test_new_email_duration_without_repeat_raises():
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        Alarm.new_email(
            summary="S",
            description="D",
            trigger=timedelta(minutes=-30),
            attendees=[vCalAddress("mailto:user@example.com")],
            duration=timedelta(minutes=5),
        )


def test_new_email_repeat_without_duration_raises():
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        Alarm.new_email(
            summary="S",
            description="D",
            trigger=timedelta(minutes=-30),
            attendees=[vCalAddress("mailto:user@example.com")],
            repeat=2,
        )
