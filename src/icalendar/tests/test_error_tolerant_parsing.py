"""Tests for error-tolerant parsing of property values."""

import pytest

from icalendar.error import BrokenCalendarProperty
from icalendar.prop import vBroken, vDDDLists, vDDDTypes, vRecur, vText


def test_properties_parsed_immediately(calendars):
    """Verify properties are parsed immediately during from_ical()."""

    cal = calendars.issue_1081_event_with_rrule
    event = cal.walk("VEVENT")[0]

    rrule = event["RRULE"]
    assert isinstance(rrule, vRecur)
    assert rrule["FREQ"] == ["DAILY"]
    assert rrule["COUNT"] == [10]


def test_params_accessible(calendars):
    """Verify params are accessible on parsed properties."""

    cal = calendars.issue_1081_tzid_param
    event = cal.walk("VEVENT")[0]

    dtstart = event["DTSTART"]

    assert dtstart.params["TZID"] == "America/New_York"


def test_broken_property_vbroken_fallback(calendars):
    """Verify broken properties fall back to vBroken."""
    cal = calendars.broken_dtstart
    event = cal.walk("VEVENT")[0]

    dtstart = event["DTSTART"]

    # Should fall back to vBroken (which is vText subclass)
    assert isinstance(dtstart, vBroken)
    assert isinstance(dtstart, vText)  # vBroken inherits from vText
    assert str(dtstart) == "INVALID-DATE"

    assert dtstart.property_name == "DTSTART"
    assert dtstart.expected_type is not None
    assert dtstart.parse_error is not None

    assert len(event.errors) == 1
    assert event.errors[0][0] == "DTSTART"


def test_broken_property_doesnt_block_others(calendars):
    """Verify one broken property doesn't prevent accessing others."""
    cal = calendars.issue_1081_invalid_start_valid_end
    event = cal.walk("VEVENT")[0]

    dtend = event["DTEND"]
    assert isinstance(dtend, vDDDTypes)
    assert dtend.dt.year == 2025

    dtstart = event["DTSTART"]
    assert isinstance(dtstart, vBroken)

    summary = event["SUMMARY"]
    assert str(summary) == "Test Event"


def test_property_to_ical(calendars):
    """Verify to_ical() works correctly with properties."""
    cal = calendars.issue_1081_event_with_rrule

    output = cal.to_ical()

    assert b"DTSTART:20250101T100000Z" in output
    assert b"RRULE:FREQ=DAILY;COUNT=10" in output
    assert b"SUMMARY:Test Event" in output


def test_multiple_properties_in_list(calendars):
    """Verify lists of properties work correctly."""
    cal = calendars.issue_1081_list_of_properties
    event = cal.walk("VEVENT")[0]

    exdates = event["EXDATE"]

    assert isinstance(exdates, list)
    assert len(exdates) == 2
    assert all(isinstance(dt, vDDDLists) for dt in exdates)


def test_property_with_tzid(calendars):
    """Verify TZID parameter is handled correctly."""

    cal = calendars.issue_1081_tzid_param
    event = cal.walk("VEVENT")[0]

    dtstart = event["DTSTART"]

    assert isinstance(dtstart, vDDDTypes)
    assert dtstart.dt.year == 2025
    assert dtstart.dt.month == 1
    assert dtstart.dt.day == 1


def test_freebusy_comma_separated_values(calendars):
    """Verify FREEBUSY comma-separated values work with error-tolerant parsing."""

    cal = calendars.issue_1081_freebusy_comma_separated
    fb = cal.walk("VFREEBUSY")[0]

    freebusy = fb["FREEBUSY"]

    assert isinstance(freebusy, list)
    assert len(freebusy) == 2


def test_empty_rdate_workaround(calendars):
    """Verify empty RDATE values are handled correctly."""
    cal = calendars.issue_1081_empty_rdate
    event = cal.walk("VEVENT")[0]

    assert "RDATE" not in event


def test_vbroken_repr(calendars):
    """Verify vBroken repr includes metadata."""
    cal = calendars.broken_dtstart
    event = cal.walk("VEVENT")[0]

    dtstart = event["DTSTART"]

    assert "vBroken" in repr(dtstart)
    assert "INVALID-DATE" in repr(dtstart)
    assert "expected_type" in repr(dtstart)
    assert "property_name" in repr(dtstart)


def test_ignore_exceptions_flag_respected(calendars):
    """Verify ignore_exceptions flag behavior."""
    # Event has ignore_exceptions=True
    cal = calendars.broken_dtstart
    event = cal.walk("VEVENT")[0]

    dtstart = event["DTSTART"]
    assert isinstance(dtstart, vBroken)
    assert len(event.errors) > 0


def test_property_str(calendars):
    """Verify __str__ works."""
    cal = calendars.issue_1081_with_summary
    event = cal.walk("VEVENT")[0]

    summary = event["SUMMARY"]
    assert str(summary) == "Test Event"


def test_vbroken_metadata(calendars):
    """Verify vBroken stores parse error metadata."""
    cal = calendars.broken_dtstart
    event = cal.walk("VEVENT")[0]
    dtstart = event["DTSTART"]

    assert isinstance(dtstart, vBroken)
    assert dtstart.property_name == "DTSTART"
    assert dtstart.expected_type is not None
    assert dtstart.parse_error is not None


def test_errors_populated_immediately(calendars):
    """Verify errors available after from_ical without property access."""
    cal = calendars.issue_1081_invalid_start_and_end
    event = cal.walk("VEVENT")[0]

    # Errors should be populated WITHOUT accessing properties
    assert len(event.errors) == 2
    assert event.errors[0][0] == "DTSTART"
    assert event.errors[1][0] == "DTEND"


def test_typeerror_handling_in_tolerant_mode(calendars):
    """Verify TypeError exceptions are caught in error-tolerant mode.

    This test addresses the concern raised in PR #1044 review that
    TypeError exceptions should be handled consistently with ValueError.
    """
    # Event has ignore_exceptions=True (error-tolerant)
    # Using RRULE with invalid type that triggers TypeError during parsing
    cal = calendars.issue_1081_invalid_rrule_freq
    event = cal.walk("VEVENT")[0]

    rrule = event["RRULE"]
    assert isinstance(rrule, vBroken)

    assert len(event.errors) >= 1
    assert any("RRULE" in error[0] for error in event.errors)


def test_parse_error_is_exception_object(calendars):
    """Verify parse_error stores the actual exception, not a string."""
    cal = calendars.broken_dtstart
    event = cal.walk("VEVENT")[0]
    dtstart = event["DTSTART"]

    assert isinstance(dtstart, vBroken)
    assert isinstance(dtstart.parse_error, Exception)


@pytest.fixture
def broken():
    return vBroken(
        "INVALID",
        property_name="DTSTART",
        expected_type="vDDDTypes",
        parse_error=ValueError("bad value"),
    )


def test_vbroken_getattr_raises_broken_calendar_property(broken):
    """Verify accessing missing attributes raises BrokenCalendarProperty."""
    with pytest.raises(BrokenCalendarProperty) as exc_info:
        broken.dt

    assert exc_info.value.__cause__ is broken.parse_error
    assert "DTSTART" in str(exc_info.value)
    assert "vDDDTypes" in str(exc_info.value)


def test_vbroken_getattr_preserves_existing_attributes(broken):
    """Verify normal attributes still work on vBroken."""
    assert broken.property_name == "DTSTART"
    assert broken.expected_type == "vDDDTypes"
    assert isinstance(broken.parse_error, ValueError)
    assert isinstance(broken.params, dict)
    assert broken.encoding is not None


def test_event_dtstart_raises_broken_calendar_property(calendars):
    """Verify event.DTSTART raises BrokenCalendarProperty for broken values."""
    cal = calendars.broken_dtstart
    event = cal.walk("VEVENT")[0]

    with pytest.raises(BrokenCalendarProperty) as exc_info:
        event.DTSTART

    assert exc_info.value.__cause__ is not None
