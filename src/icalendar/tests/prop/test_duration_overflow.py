r"""A duration too large for ``datetime.timedelta`` must raise ``InvalidCalendar``.

``DURATION_REGEX`` accepts an unbounded run of digits, but ``timedelta`` rejects
values that overflow its C implementation with ``OverflowError``. That error used
to leak out of :meth:`vDuration.from_ical`, so callers catching the documented
:exc:`ValueError` / :class:`~icalendar.error.InvalidCalendar` crashed instead.
It is now reported as an invalid duration, like any other bad value.
"""

from pathlib import Path

import pytest

from icalendar import Alarm, Calendar, FreeBusy, Journal, Todo
from icalendar.error import InvalidCalendar
from icalendar.prop import vDuration


@pytest.mark.parametrize(
    "value",
    [
        "P999999999999999999W",
        "P1000000000000000000000D",
        "PT999999999999999999999H",
    ],
)
def test_vDuration_from_ical_rejects_overflowing_duration(value):
    """An overflowing duration raises InvalidCalendar, not OverflowError."""
    with pytest.raises(InvalidCalendar):
        vDuration.from_ical(value)


def test_overflowing_duration_is_a_value_error():
    """InvalidCalendar is a ValueError, so the common except clause catches it."""
    with pytest.raises(ValueError):
        vDuration.from_ical("P999999999999999999W")


def test_overflowing_duration_in_calendar_is_recorded_not_raised():
    """A full calendar parse records the bad duration instead of crashing.

    Before the fix the ``OverflowError`` escaped the component parser (which
    only catches ``ValueError``) and aborted the whole parse. Now the value is
    handled like any other invalid property and recorded in ``errors``.
    """
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:1\r\n"
        "DTSTART:20240101T000000Z\r\n"
        "DURATION:P999999999999999999W\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    calendar = Calendar.from_ical(ics)
    event = calendar.subcomponents[0]
    assert any(name == "DURATION" for name, _ in event.errors)


def test_invalid_duration_calendar_keeps_original_value(calendars):
    """A calendar with an impractical duration keeps the raw value on to_ical.

    The value cannot be decoded to a :class:`datetime.timedelta`, so it is kept
    as a broken value. Serializing the calendar again must reproduce the
    original ``DURATION`` text unchanged rather than dropping it. Runs against
    both ``Calendar`` and ``LazyCalendar`` via the ``calendars`` fixture.
    """
    calendar = calendars.invalid_duration
    event = calendar.walk("VEVENT")[0]
    assert any(name == "DURATION" for name, _ in event.errors)
    assert b"DURATION:P999999999999999999W" in calendar.to_ical()


def test_valid_durations_still_parse():
    """The guard must not affect durations within range."""
    from datetime import timedelta

    assert vDuration.from_ical("P15DT5H0M20S") == timedelta(days=15, seconds=18020)
    assert vDuration.from_ical("P7W") == timedelta(days=49)
    assert vDuration.from_ical("-P14D") == timedelta(-14)
    assert vDuration.from_ical("P0D") == timedelta(0)
    assert vDuration.from_ical("PT0S") == timedelta(0)


@pytest.mark.parametrize("value", ["P", "PT", "+P", "-P", "+PT", "-PT"])
def test_vDuration_from_ical_rejects_duration_with_no_component(value):
    """A duration with no week, day, or time component is not zero.

    DURATION_REGEX makes every component optional, so these strings used
    to match and return timedelta(0). RFC 5545 requires one of dur-date,
    dur-time, or dur-week.
    """
    with pytest.raises(InvalidCalendar):
        vDuration.from_ical(value)


def test_empty_duration_in_calendar_is_recorded_not_zero(calendars):
    """DURATION:P stays the raw value. It is not a zero-length event.

    Runs against both ``Calendar`` and ``LazyCalendar`` via the ``calendars``
    fixture. See ``issue_1872_empty_duration.ics``.
    """
    calendar = calendars.issue_1872_empty_duration
    event = calendar.walk("VEVENT")[0]
    assert event["DURATION"] == "P"
    assert any(name == "DURATION" for name, _ in event.errors)
    assert b"DURATION:P" in calendar.to_ical()


@pytest.mark.parametrize(
    ("component", "folder"),
    [
        (Todo, "todos"),
        (Journal, "journals"),
        (Alarm, "alarms"),
        (FreeBusy, "freebusy"),
    ],
)
def test_other_components_reject_an_empty_duration(component, folder):
    """A todo, journal, alarm, and freebusy do not turn DURATION:P into zero."""
    path = Path(__file__).parents[1] / folder / "issue_1872_empty_duration.ics"
    with pytest.raises(InvalidCalendar):
        component.from_ical(path.read_bytes())
