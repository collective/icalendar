"""Duplicated singleton UTC properties return the earliest valid value.

See https://github.com/collective/icalendar/issues/1795
"""

from datetime import datetime, timezone

import pytest

from icalendar import Event, is_utc
from icalendar.error import InvalidCalendar
from icalendar.prop import vDDDTypes, vText, vUnknown

UTC = timezone.utc


def _events_by_uid(cal):
    """Map UID to event for the issue 1795 fixture calendar."""
    return {str(event["UID"]): event for event in cal.walk("VEVENT")}


def test_issue_example_returns_earliest_dtstamp(calendars):
    """The issue reproducer returns the earliest DTSTAMP, not the first encountered."""
    events = _events_by_uid(calendars.issue_1795_duplicate_single_properties)
    assert events["1795-reproducer"].stamp == datetime(2020, 5, 16, 6, 0, tzinfo=UTC)


def test_duplicate_raw_values_are_preserved_for_serialization(calendars):
    """Reading the accessor still preserves all duplicate values for serialization."""
    cal = calendars.issue_1795_duplicate_single_properties
    event = _events_by_uid(cal)["1795-reproducer"]

    assert event.stamp == datetime(2020, 5, 16, 6, 0, tzinfo=UTC)

    serialized = cal.to_ical()
    assert b"DTSTAMP:20210205T101751Z" in serialized
    assert b"DTSTAMP:20200516T060000Z" in serialized


def test_single_dtstamp_is_unchanged():
    """A single DTSTAMP keeps its existing behavior."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    assert event.stamp == datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)


@pytest.mark.parametrize("earliest_first", [True, False])
def test_duplicate_utc_dtstamps_return_earliest(earliest_first):
    """Order of occurrence does not matter, the earliest value wins."""
    early = datetime(2020, 5, 16, 6, 0, tzinfo=UTC)
    late = datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)
    event = Event()
    first, second = (early, late) if earliest_first else (late, early)
    event.add("DTSTAMP", first)
    event.add("DTSTAMP", second)
    assert event.stamp == early


def test_duplicate_with_other_timezone_returns_earliest_instant(tzp):
    """A timezone-aware duplicate is compared by instant.

    The second value uses encode=False so its timezone is preserved;
    normal add() normalizes DTSTAMP to UTC, and parsed DTSTAMP does not
    receive TZID handling.
    """
    utc_noon = datetime(2021, 1, 1, 12, 0, tzinfo=UTC)
    new_york_half_past_six = vDDDTypes(
        tzp.localize(datetime(2021, 1, 1, 6, 30), "America/New_York")
    )
    event = Event()
    event.add("DTSTAMP", utc_noon)
    event.add("DTSTAMP", new_york_half_past_six, encode=False)
    assert event.stamp == datetime(2021, 1, 1, 11, 30, tzinfo=UTC)
    assert is_utc(event.stamp)


def test_mixed_duplicates_from_parser_return_earliest(calendars):
    """A DATE counts as midnight UTC against datetime duplicates."""
    events = _events_by_uid(calendars.issue_1795_duplicate_single_properties)
    assert events["1795-mixed-duplicates"].stamp == datetime(
        2021, 1, 1, 0, 0, tzinfo=UTC
    )


@pytest.mark.parametrize("uid", ["1795-value-text", "1795-value-unknown"])
def test_explicit_value_type_decodes_like_typed(calendars, uid):
    """DTSTAMP with VALUE=TEXT or VALUE=UNKNOWN keeps its legacy decoding."""
    events = _events_by_uid(calendars.issue_1795_duplicate_single_properties)
    event = events[uid]
    assert event.stamp == datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)


def test_value_text_stays_untyped(calendars):
    """The TEXT branch of the decoder is really taken, not just the result."""
    events = _events_by_uid(calendars.issue_1795_duplicate_single_properties)
    assert isinstance(events["1795-value-text"]["DTSTAMP"], vText)
    assert isinstance(events["1795-value-unknown"]["DTSTAMP"], vUnknown)


def test_duplicate_created_returns_earliest():
    """The leniency applies to other single UTC properties, too."""
    event = Event()
    event.add("CREATED", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event.add("CREATED", datetime(2020, 5, 16, 6, 0, tzinfo=UTC))
    assert event.CREATED == datetime(2020, 5, 16, 6, 0, tzinfo=UTC)


def test_valid_item_used_despite_invalid_sibling():
    """One valid value wins over siblings that cannot be datetimes."""
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event.add("DTSTAMP", 42, encode=False)
    assert event.stamp == datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)


def test_valid_item_used_despite_malformed_text_sibling():
    """A TEXT sibling that fails to decode is ignored like a non-datetime.

    It raises ValueError, not InvalidCalendar; the duplicate path
    tolerates both, the scalar path keeps legacy behavior.
    """
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event.add("DTSTAMP", vText("not-a-date!"), encode=False)
    assert event.stamp == datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC)


def test_all_malformed_text_list_still_raises():
    """A duplicate list with no decodable value stays invalid, as before."""
    event = Event()
    event.add("DTSTAMP", vText("not-a-date!"), encode=False)
    event.add("DTSTAMP", vText("still-not-a-date!"), encode=False)
    with pytest.raises(InvalidCalendar, match="DTSTAMP must be a datetime in UTC"):
        event.stamp


def test_all_invalid_list_still_raises():
    """A duplicate list with no valid value stays invalid, as before."""
    event = Event()
    event.add("DTSTAMP", 42, encode=False)
    event.add("DTSTAMP", 43, encode=False)
    with pytest.raises(InvalidCalendar, match="DTSTAMP must be a datetime in UTC"):
        event.stamp


def test_scalar_invalid_still_raises():
    """A single value that cannot be a datetime keeps raising InvalidCalendar."""
    event = Event()
    event.add("DTSTAMP", 42, encode=False)
    with pytest.raises(InvalidCalendar, match="DTSTAMP must be a datetime in UTC"):
        event.stamp


def test_empty_list_still_raises():
    """An empty value list stays invalid, as before.

    No normal construction yields an empty list.
    """
    event = Event()
    event.add("DTSTAMP", datetime(2021, 2, 5, 10, 17, 51, tzinfo=UTC))
    event["DTSTAMP"] = []
    with pytest.raises(InvalidCalendar, match="DTSTAMP must be a datetime in UTC"):
        event.stamp
