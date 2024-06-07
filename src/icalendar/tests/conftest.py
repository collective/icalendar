try:
    from backports import zoneinfo
    # we make the tests nicer
    class ZoneInfo(zoneinfo.ZoneInfo):
        def __repr__(self):
            return f"zoneinfo.ZoneInfo(key={repr(self.key)})"
    zoneinfo.ZoneInfo = ZoneInfo
except ImportError:
    pass
import os
import pytest
import icalendar
import pytz
from datetime import datetime
from dateutil import tz
from icalendar.cal import Component, Calendar, Event, ComponentFactory
from icalendar.timezone import tzp as _tzp
from icalendar.timezone import TZP

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
        if attribute.endswith(".ics"):
            source_file = attribute
            attribute = attribute[:-4]
        else:
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

    def __contains__(self, key):
        """key in self.keys()"""
        if key.endswith(".ics"):
            key = key[:-4]
        return key in self.keys()

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
TIMEZONES_FOLDER = os.path.join(HERE, 'timezones')
EVENTS_FOLDER = os.path.join(HERE, 'events')

@pytest.fixture(scope="package")
def calendars(tzp):
    return DataSource(CALENDARS_FOLDER, icalendar.Calendar.from_ical)

@pytest.fixture(scope="package")
def timezones(tzp):
    return DataSource(TIMEZONES_FOLDER, icalendar.Timezone.from_ical)

@pytest.fixture(scope="package")
def events(tzp):
    return DataSource(EVENTS_FOLDER, icalendar.Event.from_ical)

@pytest.fixture(params=[
    pytz.utc,
    zoneinfo.ZoneInfo('UTC'),
    pytz.timezone('UTC'),
    tz.UTC,
    tz.gettz('UTC')])
def utc(request, tzp):
    return request.param

@pytest.fixture(params=[
    lambda dt, tzname: pytz.timezone(tzname).localize(dt),
    lambda dt, tzname: dt.replace(tzinfo=tz.gettz(tzname)),
    lambda dt, tzname: dt.replace(tzinfo=zoneinfo.ZoneInfo(tzname))
])
def in_timezone(request, tzp):
    return request.param


# exclude broken calendars here
ICS_FILES_EXCLUDE = (
    "big_bad_calendar.ics", "issue_104_broken_calendar.ics", "small_bad_calendar.ics",
    "multiple_calendar_components.ics", "pr_480_summary_with_colon.ics",
    "parsing_error_in_UTC_offset.ics", "parsing_error.ics",
)
ICS_FILES = [
    file_name for file_name in
    os.listdir(CALENDARS_FOLDER) + os.listdir(TIMEZONES_FOLDER) + os.listdir(EVENTS_FOLDER)
    if file_name not in ICS_FILES_EXCLUDE
]
@pytest.fixture(params=ICS_FILES)
def ics_file(tzp, calendars, timezones, events, request):
    """An example ICS file."""
    ics_file = request.param
    print("example file:", ics_file)
    for data in calendars, timezones, events:
        if ics_file in data:
            return data[ics_file]
    raise ValueError(f"Could not find file {ics_file}.")


FUZZ_V1 = [os.path.join(CALENDARS_FOLDER, key) for key in os.listdir(CALENDARS_FOLDER) if "fuzz-testcase" in key]
@pytest.fixture(params=FUZZ_V1)
def fuzz_v1_calendar(request):
    """Clusterfuzz calendars."""
    return request.param


@pytest.fixture()
def x_sometime():
    """Map x_sometime to time"""
    icalendar.cal.types_factory.types_map['X-SOMETIME'] = 'time'
    yield
    icalendar.cal.types_factory.types_map.pop('X-SOMETIME')


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
def event_component(tzp):
    """Return an event component."""
    c = Component()
    c.name = 'VEVENT'
    return c


@pytest.fixture()
def c(tzp):
    """Return an empty component."""
    c = Component()
    return c
comp = c

@pytest.fixture()
def calendar_component(tzp):
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
def calendar_with_resources(tzp):
    c = Calendar()
    c['resources'] = 'Chair, Table, "Room: 42"'
    return c


@pytest.fixture(params=["pytz", "zoneinfo"], scope="package")
def tzp_name(request):
    """The name of the timezone provider."""
    return request.param


@pytest.fixture(scope="package")
def tzp(tzp_name):
    """The time zone provider."""
    _tzp.use(tzp_name)
    yield _tzp
    _tzp.use_default()


@pytest.fixture(params=["pytz", "zoneinfo"])
def other_tzp(request, tzp):
    """This is annother timezone provider.

    The purpose here is to cross test: pytz <-> zoneinfo.
    tzp as parameter makes sure we test the cross product.
    """
    tzp = TZP(request.param)
    return tzp


@pytest.fixture()
def pytz_only(tzp):
    """Skip tests that are not running under pytz."""
    if not tzp.uses_pytz():
        pytest.skip("Not using pytz. Skipping this test.")


@pytest.fixture()
def zoneinfo_only(tzp):
    """Skip tests that are not running under pytz."""
    if not tzp.uses_zoneinfo():
        pytest.skip("Not using zoneinfo. Skipping this test.")
