"""This tests the properties of components and their types."""
from datetime import date, datetime, timedelta

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore PGH003

from icalendar import (
    Event,
    IncompleteComponent,
    InvalidCalendar,
    Journal,
    vDDDTypes,
)
from icalendar.prop import vDuration


@pytest.fixture()
def event():
    """The event to test."""
    return Event()

@pytest.fixture(params=[
        datetime(2022, 7, 22, 12, 7),
        date(2022, 7, 22),
        datetime(2022, 7, 22, 13, 7, tzinfo=ZoneInfo("Europe/Paris")),
    ])
def dtstart(request, set_event_start, event):
    """Start of the event."""
    set_event_start(event, request.param)
    return request.param


def _set_event_start_init(event, start):
    """Create the event with the __init__ method."""
    d = dict(event)
    d["dtstart"] = vDDDTypes(start)
    event.clear()
    event.update(Event(d))

def _set_event_dtstart(event, start):
    """Create the event with the dtstart property."""
    event.DTSTART = start

def _set_event_start_attr(event, start):
    """Create the event with the dtstart property."""
    event.start = start

def _set_event_start_ics(event, start):
    """Create the event with the start property."""
    event.add("dtstart", start)
    ics = event.to_ical().decode()
    print(ics)
    event.clear()
    event.update(Event.from_ical(ics))

@pytest.fixture(params=[_set_event_start_init, _set_event_start_ics, _set_event_dtstart, _set_event_start_attr])
def set_event_start(request):
    """Create a new event."""
    return request.param

def test_event_dtstart(dtstart, event):
    """Test the start of events."""
    assert event.DTSTART == dtstart


def test_event_start(dtstart, event):
    """Test the start of events."""
    assert event.start == dtstart


invalid_start_event_1 = Event()
invalid_start_event_1.add("dtstart", datetime(2022, 7, 22, 12, 7))
invalid_start_event_1.add("dtstart", datetime(2022, 7, 22, 12, 8))
invalid_start_event_2 = Event.from_ical(invalid_start_event_1.to_ical())
invalid_start_event_3 = Event()
invalid_start_event_3.add("DTSTART", (date(2018, 1, 1), date(2018, 2, 1)))

@pytest.mark.parametrize("invalid_event", [invalid_start_event_1, invalid_start_event_2, invalid_start_event_3])
def test_multiple_dtstart(invalid_event):
    """Check that we get the right error."""
    with pytest.raises(InvalidCalendar):
        invalid_event.start  # noqa: B018
    with pytest.raises(InvalidCalendar):
        invalid_event.DTSTART  # noqa: B018

def test_no_dtstart():
    """DTSTART is optional.

    The following is REQUIRED if the component
    appears in an iCalendar object that doesn't
    specify the "METHOD" property; otherwise, it
    is OPTIONAL; in any case, it MUST NOT occur
    more than once.
    """
    assert Event().DTSTART is None
    with pytest.raises(IncompleteComponent):
        Event().start  # noqa: B018


@pytest.fixture(params=[
        datetime(2022, 7, 22, 12, 8),
        date(2022, 7, 23),
        datetime(2022, 7, 22, 14, 7, tzinfo=ZoneInfo("Europe/Paris")),
    ])
def dtend(request, set_event_end, event):
    """end of the event."""
    set_event_end(event, request.param)
    return request.param


def _set_event_end_init(event, end):
    """Create the event with the __init__ method."""
    d = dict(event)
    d["dtend"] = vDDDTypes(end)
    event.clear()
    event.update(Event(d))

def _set_event_dtend(event, end):
    """Create the event with the dtend property."""
    event.DTEND = end

def _set_event_end_attr(event, end):
    """Create the event with the dtend property."""
    event.end = end

def _set_event_end_ics(event, end):
    """Create the event with the end property."""
    event.add("dtend", end)
    ics = event.to_ical().decode()
    print(ics)
    event.clear()
    event.update(Event.from_ical(ics))

@pytest.fixture(params=[_set_event_end_init, _set_event_end_ics, _set_event_dtend, _set_event_end_attr])
def set_event_end(request):
    """Create a new event."""
    return request.param

def test_event_dtend(dtend, event):
    """Test the end of events."""
    assert event.DTEND == dtend  # noqa: SIM300


def test_event_end(dtend, event):
    """Test the end of events."""
    assert event.end == dtend


@pytest.mark.parametrize("attr", ["DTSTART", "DTEND"])
def test_delete_attr(event, dtstart, dtend, attr):
    delattr(event, attr)
    assert getattr(event, attr) is None
    delattr(event, attr)


def _set_duration_vdddtypes(event:Event, duration:timedelta):
    """Set the vDDDTypes value"""
    event["DURATION"] = vDDDTypes(duration)

def _set_duration_add(event:Event, duration:timedelta):
    """Set the vDDDTypes value"""
    event.add("DURATION", duration)

def _set_duration_vduration(event:Event, duration:timedelta):
    """Set the vDDDTypes value"""
    event["DURATION"] = vDuration(duration)

@pytest.fixture(params=[_set_duration_vdddtypes, _set_duration_add, _set_duration_vduration])
def duration(event, dtstart, request):
    """... events have a DATE value type for the "DTSTART" property ...
    If such a "VEVENT" has a "DURATION"
    property, it MUST be specified as a "dur-day" or "dur-week" value.
    """
    duration = timedelta(hours=1) if isinstance(dtstart, datetime) else timedelta(days=2)
    request.param(event, duration)
    return duration

def test_start_and_duration(event, dtstart, duration):
    """Check calculation of end with duration."""
    dur = event.end - event.start
    assert dur == duration
    assert event.duration == duration

# The "VEVENT" is also the calendar component used to specify an
# anniversary or daily reminder within a calendar.  These events
# have a DATE value type for the "DTSTART" property instead of the
# default value type of DATE-TIME.  If such a "VEVENT" has a "DTEND"
# property, it MUST be specified as a DATE value also.
invalid_event_end_1 = Event()
invalid_event_end_1.add("DTSTART", datetime(2024, 1, 1, 10, 20))
invalid_event_end_1.add("DTEND", date(2024, 1, 1))
invalid_event_end_2 = Event()
invalid_event_end_2.add("DTEND", datetime(2024, 1, 1, 10, 20))
invalid_event_end_2.add("DTSTART", date(2024, 1, 1))
invalid_event_end_3 = Event()
invalid_event_end_3.add("DTEND", datetime(2024, 1, 1, 10, 20))
invalid_event_end_3.add("DTSTART", datetime(2024, 1, 1, 10, 20))
invalid_event_end_3.add("DURATION", timedelta(days=1))
invalid_event_end_4 = Event()
invalid_event_end_4.add("DTSTART", date(2024, 1, 1))
invalid_event_end_4.add("DURATION", timedelta(hours=1))
@pytest.mark.parametrize(
    ("invalid_event", "message"),
    [
        (invalid_event_end_1, "DTSTART and DTEND must be of the same type, either date or datetime."),
        (invalid_event_end_2, "DTSTART and DTEND must be of the same type, either date or datetime."),
        (invalid_event_end_3, "Only one of DTEND and DURATION may be in a VEVENT, not both."),
        (invalid_event_end_4, "When DTSTART is a date, DURATION must be of days or weeks."),
    ]
)
@pytest.mark.parametrize("attr", ["start", "end"])
def test_invalid_event(invalid_event, message, attr):
    """Test that the end and start throuw the right error."""
    with pytest.raises(InvalidCalendar) as e:
        getattr(invalid_event, attr)
    assert e.value.args[0] == message

def test_duration_zero():
    """
    For cases where a "VEVENT" calendar component
    specifies a "DTSTART" property with a DATE-TIME value type but no
    "DTEND" property, the event ends on the same calendar date and
    time of day specified by the "DTSTART" property.
    """
    event = Event()
    event.start = datetime(2024, 10, 11, 10, 20)
    assert event.end == event.start
    assert event.duration == timedelta(days=0)

def test_duration_one_day():
    """
    For cases where a "VEVENT" calendar component
    specifies a "DTSTART" property with a DATE value type but no
    "DTEND" nor "DURATION" property, the event's duration is taken to
    be one day
    """
    event = Event()
    event.start = date(2024, 10, 11)
    assert event.end == event.start + timedelta(days=1)
    assert event.duration == timedelta(days=1)


incomplete_event_1 = Event()
incomplete_event_2 = Event()
incomplete_event_2.add("DURATION", timedelta(hours=1))

@pytest.mark.parametrize("incomplete_event_end", [incomplete_event_1, incomplete_event_2])
@pytest.mark.parametrize("attr", ["start", "end", "duration"])
def test_incomplete_event(incomplete_event_end, attr):
    """Test that the end throws the right error."""
    with pytest.raises(IncompleteComponent):
        getattr(incomplete_event_end, attr)


@pytest.mark.parametrize(
    "invalid_value",
    [
        object(),
        timedelta(days=1),
        (datetime(2024, 10, 11, 10, 20), timedelta(days=1)),
    ]
)
@pytest.mark.parametrize(
    ("Component", "attr"),
    [
        (Event,"start"),
        (Event,"end"),
        (Event,"DTSTART"),
        (Event,"DTEND"),
        (Journal,"start"),
        (Journal,"end"),
        (Journal,"DTSTART"),
    ]
)
def test_set_invalid_start(invalid_value, attr, Component):
    """Check that we get the right error.

    - other types that vDDDTypes accepts
    - object
    """
    event = Component()
    with pytest.raises(TypeError) as e:
        setattr(event, attr, invalid_value)
    assert e.value.args[0] == f"Use datetime or date, not {type(invalid_value).__name__}."


def setitem(d:dict, key, value):
    d[key] = value

@pytest.mark.parametrize(
    "invalid_value",
    [
        object(),
        None,
        (datetime(2024, 10, 11, 10, 20), timedelta(days=1)),
        date(2012, 2, 2),
        datetime(2022, 2, 2),
    ]
)
def test_check_invalid_duration(invalid_value):
    """Check that we get the right error."""
    event = Event()
    event["DURATION"] = invalid_value
    with pytest.raises(InvalidCalendar) as e:
        event.DURATION  # noqa: B018
    assert e.value.args[0] == f"DURATION must be a timedelta, not {type(invalid_value).__name__}."


def test_setting_the_end_deletes_the_duration():
    """Setting the end should not break the event."""
    event = Event()
    event.DTSTART = datetime(2024, 10, 11, 10, 20)
    event.DURATION = timedelta(days=1)
    event.DTEND = datetime(2024, 10, 11, 10, 21)
    assert "DURATION" not in event
    assert event.DURATION is None
    assert event.DTEND == datetime(2024, 10, 11, 10, 21)


def test_setting_duration_deletes_the_end():
    """Setting the duration should not break the event."""
    event = Event()
    event.DTSTART = datetime(2024, 10, 11, 10, 20)
    event.DTEND = datetime(2024, 10, 11, 10, 21)
    event.DURATION = timedelta(days=1)
    assert "DTEND" not in event
    assert event.DTEND is None
    assert event.DURATION == timedelta(days=1)

valid_values = pytest.mark.parametrize(
    ("attr", "value"),
    [
        ("DTSTART", datetime(2024, 10, 11, 10, 20)),
        ("DTEND", datetime(2024, 10, 11, 10, 20)),
        ("DURATION", timedelta(days=1)),
    ]
)
@valid_values
def test_setting_to_none_deletes_value(attr, value):
    """Setting attributes to None deletes them."""
    event = Event()
    setattr(event, attr, value)
    assert attr in event
    assert getattr(event, attr) == value
    setattr(event, attr, None)
    assert attr not in event


@valid_values
def test_setting_a_value_twice(attr, value):
    """Setting attributes twice replaces them."""
    event = Event()
    setattr(event, attr, value + timedelta(days=1))
    setattr(event, attr, value)
    assert getattr(event, attr) == value


@pytest.mark.parametrize("attr", ["DTSTART", "DTEND", "DURATION"])
def test_invalid_none(attr):
    """Special case for None."""
    event = Event()
    event[attr] = None
    with pytest.raises(InvalidCalendar):
        getattr(event, attr)

@pytest.mark.parametrize("attr", ["DTSTART", "end", "start"])
@pytest.mark.parametrize("start", [
    datetime(2024, 10, 11, 10, 20),
    date(2024, 10, 11),
    datetime(2024, 10, 11, 10, 20, tzinfo=ZoneInfo("Europe/Paris")),
])
def test_journal_start(start, attr):
    """Test that we can set the start of a journal."""
    j = Journal()
    setattr(j, attr, start)
    assert start == j.DTSTART
    assert j.start == start
    assert j.end == start
    assert j.duration == timedelta(0)

@pytest.mark.parametrize("attr", ["start", "end"])
def test_delete_journal_start(attr):
    """Delete the start of the journal."""
    j = Journal()
    j.start = datetime(2010, 11, 12, 13, 14)
    j.DTSTART = None
    assert j.DTSTART is None
    assert "DTSTART" not in j
    with pytest.raises(IncompleteComponent):
        getattr(j, attr)

def setting_twice_does_not_duplicate_the_entry():
    j = Journal()
    j.DTSTART = date(2024, 1,1 )
    j.DTSTART = date(2024, 1, 3)
    assert date(2024, 1, 3) == j.DTSTART
    assert j.start == date(2024, 1, 3)
    assert j.end == date(2024, 1, 3)

