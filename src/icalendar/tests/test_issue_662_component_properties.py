"""This tests the properties of components and their types."""
from datetime import date, datetime, timedelta

import pytest
from zoneinfo import ZoneInfo

from icalendar import (
    Event,
    IncompleteComponent,
    InvalidCalendar,
    vDDDTypes,
)
from icalendar.prop import vDuration


@pytest.fixture
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
    event.dtstart = start

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
    assert event.dtstart == dtstart


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
        invalid_event.dtstart  # noqa: B018

def test_no_dtstart():
    """DTSTART is optional.

    The following is REQUIRED if the component
    appears in an iCalendar object that doesn't
    specify the "METHOD" property; otherwise, it
    is OPTIONAL; in any case, it MUST NOT occur
    more than once.
    """
    assert Event().dtstart is None
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
    event.dtend = end

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
    assert event.dtend == dtend


def test_event_end(dtend, event):
    """Test the end of events."""
    assert event.end == dtend


@pytest.mark.parametrize("attr", ["dtstart", "dtend"])
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

def test_default_duration(event, dtstart):
    """Check that the end can be computed if a start is given."""

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
    ("incomplete_event_end", "message"),
    [
        (invalid_event_end_1, "DTSTART and DTEND must have the same type."),
        (invalid_event_end_2, "DTSTART and DTEND must have the same type."),
        (invalid_event_end_3, "DURATION and DTEND cannot be there at the same time."),
        (invalid_event_end_4, "When DTSTART is a date, DURATION must be of days or weeks."),
    ]
)
@pytest.mark.parametrize("attr", ["start", "end"])
def test_invalid_event(incomplete_event_end, message, attr):
    """Test that the end and start throuw the right error."""
    with pytest.raises(InvalidCalendar) as e:
        getattr(incomplete_event_end, attr)
    assert e.value.args[0] == message

def test_duration_one_day():
    """

    For cases where a "VEVENT" calendar component
    specifies a "DTSTART" property with a DATE value type but no
    "DTEND" nor "DURATION" property, the event's duration is taken to
    be one day
    """
    

incomplete_event_1 = Event()
incomplete_event_2 = Event()
incomplete_event_2.add("DURATION", timedelta(hours=1))

@pytest.mark.parametrize("incomplete_event_end", [incomplete_event_1, incomplete_event_2])
def test_incomplete_event(incomplete_event_end):
    """Test that the end throuws the right error."""
    with pytest.raises(IncompleteComponent):
        incomplete_event_end.end  # noqa: B018