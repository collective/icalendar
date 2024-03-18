import os
import pytest
import icalendar
import pytz
from datetime import datetime
from dateutil import tz
try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo
from icalendar.cal import Component, Calendar, Event, ComponentFactory


class DataSource:
    '''A collection of parsed ICS elements (e.g calendars, timezones, events)'''
    def __init__(self, data_source_folder, parser):
        self._parser = parser
        self._data_source_folder = data_source_folder

    def keys(self):
        """Return all the files that could be used."""
        return [file[:-4] for file in os.listdir(self._data_source_folder) if file.lower().endswith(".ics")]

    def __getitem__(self, attribute):
        """Parse a file and return the result stored in the attribute."""
        source_file = attribute + '.ics'
        source_path = os.path.join(self._data_source_folder, source_file)
        if not os.path.isfile(source_path):
            raise AttributeError(f"{source_path} does not exist.")
        with open(source_path, 'rb') as f:
            raw_ics = f.read()
        source = self._parser(raw_ics)
        if not isinstance(source, list):
            source.raw_ics = raw_ics
        self.__dict__[attribute] = source
        return source

    def __getattr__(self, key):
        return self[key]

    def __repr__(self):
        return repr(self.__dict__)

    @property
    def multiple(self):
        """Return a list of all components parsed."""
        return self.__class__(self._data_source_folder, lambda data: self._parser(data, multiple=True))

HERE = os.path.dirname(__file__)
CALENDARS_FOLDER = os.path.join(HERE, 'calendars')
CALENDARS = DataSource(CALENDARS_FOLDER, icalendar.Calendar.from_ical)
TIMEZONES_FOLDER = os.path.join(HERE, 'timezones')
TIMEZONES = DataSource(TIMEZONES_FOLDER, icalendar.Timezone.from_ical)
EVENTS_FOLDER = os.path.join(HERE, 'events')
EVENTS = DataSource(EVENTS_FOLDER, icalendar.Event.from_ical)

@pytest.fixture()
def calendars():
    return CALENDARS

@pytest.fixture()
def timezones():
    return TIMEZONES

@pytest.fixture()
def events():
    return EVENTS

@pytest.fixture(params=[
    pytz.utc,
    zoneinfo.ZoneInfo('UTC'),
    pytz.timezone('UTC'),
    tz.UTC,
    tz.gettz('UTC')])
def utc(request):
    return request.param

@pytest.fixture(params=[
    lambda dt, tzname: pytz.timezone(tzname).localize(dt),
    lambda dt, tzname: dt.replace(tzinfo=tz.gettz(tzname)),
    lambda dt, tzname: dt.replace(tzinfo=zoneinfo.ZoneInfo(tzname))
])
def in_timezone(request):
    return request.param


ICS_FILES = [
    (data, key)
    for data in [CALENDARS, TIMEZONES, EVENTS]
    for key in data.keys() if key not in
    ( # exclude broken calendars here
        "big_bad_calendar", "issue_104_broken_calendar", "small_bad_calendar",
        "multiple_calendar_components", "pr_480_summary_with_colon",
        "parsing_error_in_UTC_offset", "parsing_error",
    )
]
@pytest.fixture(params=ICS_FILES)
def ics_file(request):
    """An example ICS file."""
    data, key = request.param
    print(key)
    return data[key]


FUZZ_V1 = [os.path.join(CALENDARS_FOLDER, key) for key in os.listdir(CALENDARS_FOLDER) if "fuzz-testcase" in key]
@pytest.fixture(params=FUZZ_V1)
def fuzz_v1_calendar(request):
    """Clusterfuzz calendars."""
    return request.param


@pytest.fixture()
def factory():
    """Return a new component factory."""
    return icalendar.ComponentFactory()


@pytest.fixture()
def vUTCOffset_ignore_exceptions():
    icalendar.vUTCOffset.ignore_exceptions = True
    yield
    icalendar.vUTCOffset.ignore_exceptions = False


@pytest.fixture()
def event_component():
    """Return an event component."""
    c = Component()
    c.name = 'VEVENT'
    return c


@pytest.fixture()
def c():
    """Return an empty component."""
    c = Component()
    return c
comp = c

@pytest.fixture()
def calendar_component():
    """Return an empty component."""
    c = Component()
    c.name = 'VCALENDAR'
    return c


@pytest.fixture()
def filled_event_component(c, calendar_component):
    """Return an event with some values and add it to calendar_component."""
    e = Component(summary='A brief history of time')
    e.name = 'VEVENT'
    e.add('dtend', '20000102T000000', encode=0)
    e.add('dtstart', '20000101T000000', encode=0)
    calendar_component.add_component(e)
    return e


@pytest.fixture()
def calendar_with_resources():
    c = Calendar()
    c['resources'] = 'Chair, Table, "Room: 42"'
    return c
