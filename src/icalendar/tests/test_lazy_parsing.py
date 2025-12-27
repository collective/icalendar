"""Tests for lazy parsing of property values."""

from icalendar import Calendar, Event
from icalendar.cal.lazy import LazyProperty
from icalendar.caselessdict import CaselessDict
from icalendar.prop import vDDDLists, vDDDTypes, vRecur, vText


def test_lazy_property_defers_parsing():
    """Verify properties are not parsed during from_ical()."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:20250101T100000Z
RRULE:FREQ=DAILY;COUNT=10
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access raw dict via CaselessDict.__getitem__ to avoid Component's override
    raw_rrule = CaselessDict.__getitem__(event, "RRULE")

    # Should be LazyProperty before access
    assert isinstance(raw_rrule, LazyProperty)
    assert raw_rrule._parsed_value is None


def test_lazy_property_parsed_on_access():
    """Verify properties are parsed on first access."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:20250101T100000Z
RRULE:FREQ=DAILY;COUNT=10
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access through __getitem__ triggers parsing
    rrule = event["RRULE"]

    # Should be parsed vRecur object
    assert isinstance(rrule, vRecur)
    assert rrule["FREQ"] == ["DAILY"]
    assert rrule["COUNT"] == [10]


def test_params_accessible_without_parsing():
    """Verify params are accessible without triggering parse."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART;TZID=America/New_York:20250101T100000
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access raw property
    raw_dtstart = CaselessDict.__getitem__(event, "DTSTART")

    # Should be LazyProperty
    assert isinstance(raw_dtstart, LazyProperty)

    # Can access params without parsing
    assert raw_dtstart.params["TZID"] == "America/New_York"
    assert raw_dtstart._parsed_value is None  # Still not parsed


def test_broken_property_vtext_fallback():
    """Verify broken properties fall back to vText."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:INVALID-DATE-FORMAT
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access broken property
    dtstart = event["DTSTART"]

    # Should fall back to vText
    assert isinstance(dtstart, vText)
    assert str(dtstart) == "INVALID-DATE-FORMAT"

    # Error should be recorded
    assert len(event.errors) == 1
    assert event.errors[0][0] == "DTSTART"
    assert "INVALID-DATE-FORMAT" in event.errors[0][1]


def test_broken_property_doesnt_block_others():
    """Verify one broken property doesn't prevent accessing others."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:INVALID-DATE
DTEND:20250102T120000Z
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access valid property should work
    dtend = event["DTEND"]
    assert isinstance(dtend, vDDDTypes)
    assert dtend.dt.year == 2025

    # Access broken property should work (as vText)
    dtstart = event["DTSTART"]
    assert isinstance(dtstart, vText)

    # Other properties accessible
    summary = event["SUMMARY"]
    assert str(summary) == "Test Event"


def test_lazy_property_equality():
    """Verify equality comparisons work with lazy properties."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal1 = Calendar.from_ical(ical_str)
    cal2 = Calendar.from_ical(ical_str)

    event1 = cal1.walk("VEVENT")[0]
    event2 = cal2.walk("VEVENT")[0]

    # Equality should work
    assert event1["SUMMARY"] == event2["SUMMARY"]
    assert event1["SUMMARY"] == "Test Event"


def test_lazy_property_to_ical():
    """Verify to_ical() works correctly with lazy properties."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:20250101T100000Z
RRULE:FREQ=DAILY;COUNT=10
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)

    # to_ical() should work without explicit access
    output = cal.to_ical()

    # Should contain all properties
    assert b"DTSTART:20250101T100000Z" in output
    assert b"RRULE:FREQ=DAILY;COUNT=10" in output
    assert b"SUMMARY:Test Event" in output


def test_multiple_lazy_properties_in_list():
    """Verify lists of lazy properties work correctly."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:20250101T100000Z
EXDATE:20250105T100000Z
EXDATE:20250106T100000Z
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access list of properties
    exdates = event["EXDATE"]

    # Should be list of vDDDLists
    assert isinstance(exdates, list)
    assert len(exdates) == 2
    assert all(isinstance(dt, vDDDLists) for dt in exdates)


def test_lazy_property_with_tzid():
    """Verify TZID parameter is handled correctly."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART;TZID=America/New_York:20250101T100000
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access datetime with TZID
    dtstart = event["DTSTART"]

    # Should be properly parsed with timezone
    assert isinstance(dtstart, vDDDTypes)
    assert dtstart.dt.year == 2025
    assert dtstart.dt.month == 1
    assert dtstart.dt.day == 1


def test_freebusy_comma_separated_values():
    """Verify FREEBUSY comma-separated values work with lazy parsing."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VFREEBUSY
UID:test-123
DTSTART:20250101T000000Z
DTEND:20250102T000000Z
FREEBUSY:20250101T100000Z/20250101T120000Z,20250101T140000Z/20250101T160000Z
END:VFREEBUSY
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    fb = cal.walk("VFREEBUSY")[0]

    # Access FREEBUSY list
    freebusy = fb["FREEBUSY"]

    # Should be list of periods
    assert isinstance(freebusy, list)
    assert len(freebusy) == 2


def test_empty_rdate_workaround():
    """Verify empty RDATE values are handled correctly."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:20250101T100000Z
RDATE:
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # RDATE should not be in the event
    assert "RDATE" not in event


def test_lazy_property_caching():
    """Verify parsed values are cached after first access."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
RRULE:FREQ=DAILY;COUNT=10
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # First access
    rrule1 = event["RRULE"]

    # Access raw dict to check caching
    raw_rrule = super(Event, event).__getitem__("RRULE")

    # Should no longer be LazyProperty
    assert not isinstance(raw_rrule, LazyProperty)
    assert isinstance(raw_rrule, vRecur)

    # Second access should return same cached object
    rrule2 = event["RRULE"]
    assert rrule1 is rrule2


def test_lazy_property_repr():
    """Verify LazyProperty repr works before and after parsing."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    # Access raw property
    raw_summary = CaselessDict.__getitem__(event, "SUMMARY")

    # Repr before parsing
    assert "LazyProperty" in repr(raw_summary)
    assert "SUMMARY" in repr(raw_summary)

    # Access to trigger parsing
    summary = event["SUMMARY"]

    # Repr after parsing (through the parsed object)
    assert "Test Event" in repr(summary)


def test_ignore_exceptions_flag_respected():
    """Verify ignore_exceptions flag behavior."""
    # Event has ignore_exceptions=True
    ical_str_event = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
DTSTART:INVALID
SUMMARY:Test
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str_event)
    event = cal.walk("VEVENT")[0]

    # Should not raise, falls back to vText
    dtstart = event["DTSTART"]
    assert isinstance(dtstart, vText)
    assert len(event.errors) > 0


def test_lazy_property_str():
    """Verify __str__ delegation works."""
    ical_str = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
BEGIN:VEVENT
UID:test-123
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR"""

    cal = Calendar.from_ical(ical_str)
    event = cal.walk("VEVENT")[0]

    summary = event["SUMMARY"]
    assert str(summary) == "Test Event"
