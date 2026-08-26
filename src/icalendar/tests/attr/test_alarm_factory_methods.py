"""Tests for Alarm.new_display(), Alarm.new_audio(), and Alarm.new_email()."""

from datetime import datetime, timedelta, timezone

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.error import InvalidCalendar
from icalendar.prop import vCalAddress
from icalendar.prop.binary import vBinary
from icalendar.prop.text import vText
from icalendar.prop.uri import vUri

_TRIGGER = timedelta(minutes=-15)
_ATTENDEE = vCalAddress("mailto:a@example.com")


def _display(**kw) -> Alarm:
    return Alarm.new_display("Reminder", _TRIGGER, **kw)


def _audio(**kw) -> Alarm:
    return Alarm.new_audio(_TRIGGER, **kw)


def _email(**kw) -> Alarm:
    return Alarm.new_email("Subject", "Body", _TRIGGER, [_ATTENDEE], **kw)


_ALL_FACTORIES = pytest.mark.parametrize(
    "factory", [_display, _audio, _email], ids=["new_display", "new_audio", "new_email"]
)


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


@pytest.mark.parametrize(
    "alarm_fn",
    [
        lambda: Alarm.new_display(
            "desc", timedelta(minutes=-5), duration=timedelta(minutes=1)
        ),
        lambda: Alarm.new_audio(timedelta(minutes=-5), duration=timedelta(minutes=1)),
        lambda: Alarm.new_email(
            "S",
            "D",
            timedelta(minutes=-30),
            vCalAddress("mailto:a@example.com"),
            duration=timedelta(minutes=5),
        ),
    ],
    ids=["display", "audio", "email"],
)
def test_duration_without_repeat_raises(alarm_fn):
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        alarm_fn()


@pytest.mark.parametrize(
    "alarm_fn",
    [
        lambda: Alarm.new_display("desc", timedelta(minutes=-5), repeat=3),
        lambda: Alarm.new_audio(timedelta(minutes=-5), repeat=3),
        lambda: Alarm.new_email(
            "S",
            "D",
            timedelta(minutes=-30),
            vCalAddress("mailto:a@example.com"),
            repeat=2,
        ),
    ],
    ids=["display", "audio", "email"],
)
def test_repeat_without_duration_raises(alarm_fn):
    with pytest.raises(InvalidCalendar, match="DURATION and REPEAT"):
        alarm_fn()


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
    alarm = Alarm.new_audio(timedelta(minutes=-5), attachments=uri)
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


def test_new_audio_with_bytes_attach():
    data = b"\x00\x01\x02\x03"
    alarm = Alarm.new_audio(timedelta(minutes=-5), attachments=data)
    assert isinstance(alarm["ATTACH"], vBinary)
    assert alarm["ATTACH"] == vBinary(data)


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
    assert str(alarm.attendees[0]) == "mailto:a@example.com"
    assert str(alarm.attendees[1]) == "mailto:b@example.com"


def test_new_email_with_attachment():
    alarm = Alarm.new_email(
        summary="S",
        description="D",
        trigger=timedelta(minutes=-30),
        attendees=[vCalAddress("mailto:user@example.com")],
        attachments=["https://example.com/file.pdf"],
    )
    assert "ATTACH" in alarm
    assert str(alarm["ATTACH"]) == "https://example.com/file.pdf"


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


def test_new_email_single_attendee():
    alarm = Alarm.new_email(
        summary="S",
        description="D",
        trigger=timedelta(minutes=-30),
        attendees=vCalAddress("mailto:user@example.com"),
    )
    assert len(alarm.attendees) == 1
    assert str(alarm.attendees[0]) == "mailto:user@example.com"


def test_new_email_single_attachment():
    alarm = Alarm.new_email(
        summary="S",
        description="D",
        trigger=timedelta(minutes=-30),
        attendees=[vCalAddress("mailto:user@example.com")],
        attachments="https://example.com/file.pdf",
    )
    assert "ATTACH" in alarm
    assert str(alarm["ATTACH"]) == "https://example.com/file.pdf"


# Shared parameters: uid, links, related_to, concepts


@_ALL_FACTORIES
def test_factory_uid_is_set(factory):
    alarm = factory(uid="test-alarm-uid-001")
    assert alarm.uid == "test-alarm-uid-001"
    assert "UID" in alarm


@_ALL_FACTORIES
def test_factory_uid_none_omits_property(factory):
    alarm = factory(uid=None)
    assert "UID" not in alarm


@_ALL_FACTORIES
def test_factory_links_single(factory):
    link = vUri("https://example.com/event")
    alarm = factory(links=[link])
    assert alarm.links == [link]


@_ALL_FACTORIES
def test_factory_links_string_is_converted(factory):
    alarm = factory(links=["https://example.com/event"])
    assert alarm.links == [vUri("https://example.com/event")]


@_ALL_FACTORIES
def test_factory_links_none_is_empty(factory):
    alarm = factory(links=None)
    assert alarm.links == []
    assert "LINK" not in alarm


@_ALL_FACTORIES
def test_factory_related_to_single(factory):
    rel = vText("some-uid-ref")
    alarm = factory(related_to=[rel])
    assert alarm.related_to == [rel]


@_ALL_FACTORIES
def test_factory_related_to_string_is_converted(factory):
    alarm = factory(related_to=["some-uid-ref"])
    assert alarm.related_to == [vText("some-uid-ref")]


@_ALL_FACTORIES
def test_factory_related_to_none_is_empty(factory):
    alarm = factory(related_to=None)
    assert alarm.related_to == []
    assert "RELATED-TO" not in alarm


@_ALL_FACTORIES
def test_factory_concepts_single(factory):
    concept = vUri("https://example.com/concept")
    alarm = factory(concepts=[concept])
    assert alarm.concepts == [concept]


@_ALL_FACTORIES
def test_factory_concepts_string_is_converted(factory):
    alarm = factory(concepts=["https://example.com/concept"])
    assert alarm.concepts == [vUri("https://example.com/concept")]


@_ALL_FACTORIES
def test_factory_concepts_none_is_empty(factory):
    alarm = factory(concepts=None)
    assert alarm.concepts == []
    assert "CONCEPT" not in alarm


# Alarm.new shared parameters: uid, links, related_to, concepts


def test_alarm_new_uid_is_set():
    alarm = Alarm.new(uid="test-alarm-uid-001")
    assert alarm.uid == "test-alarm-uid-001"
    assert "UID" in alarm


def test_alarm_new_uid_none_omits_property():
    alarm = Alarm.new(uid=None)
    assert "UID" not in alarm


def test_alarm_new_links_single():
    link = vUri("https://example.com/event")
    alarm = Alarm.new(links=[link])
    assert alarm.links == [link]


def test_alarm_new_links_string_is_converted():
    alarm = Alarm.new(links=["https://example.com/event"])
    assert alarm.links == [vUri("https://example.com/event")]


def test_alarm_new_links_none_is_empty():
    alarm = Alarm.new(links=None)
    assert alarm.links == []
    assert "LINK" not in alarm


def test_alarm_new_related_to_single():
    rel = vText("some-uid-ref")
    alarm = Alarm.new(related_to=[rel])
    assert alarm.related_to == [rel]


def test_alarm_new_related_to_string_is_converted():
    alarm = Alarm.new(related_to=["some-uid-ref"])
    assert alarm.related_to == [vText("some-uid-ref")]


def test_alarm_new_related_to_none_is_empty():
    alarm = Alarm.new(related_to=None)
    assert alarm.related_to == []
    assert "RELATED-TO" not in alarm


def test_alarm_new_concepts_single():
    concept = vUri("https://example.com/concept")
    alarm = Alarm.new(concepts=[concept])
    assert alarm.concepts == [concept]


def test_alarm_new_concepts_string_is_converted():
    alarm = Alarm.new(concepts=["https://example.com/concept"])
    assert alarm.concepts == [vUri("https://example.com/concept")]


def test_alarm_new_concepts_none_is_empty():
    alarm = Alarm.new(concepts=None)
    assert alarm.concepts == []
    assert "CONCEPT" not in alarm


@pytest.mark.parametrize(
    ("attendees", "expected"),
    [
        ("first@example.com", "mailto:first@example.com"),
        (["first@example.com"], "mailto:first@example.com"),
        ("mailto:second@example.net", "mailto:second@example.net"),
        (["mailto:second@example.net"], "mailto:second@example.net"),
    ],
)
def test_new_email_string_attendee_normalizes(attendees, expected):
    """Plain and mailto: string attendees, singleton or in a list, normalize to vCalAddress."""
    alarm = Alarm.new_email(
        summary="S",
        description="D",
        trigger=timedelta(minutes=-30),
        attendees=attendees,
    )
    assert isinstance(alarm.attendees[0], vCalAddress)
    assert str(alarm.attendees[0]) == expected
