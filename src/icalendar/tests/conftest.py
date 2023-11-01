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

class DataSource:
    '''A collection of parsed ICS elements (e.g calendars, timezones, events)'''
    def __init__(self, data_source_folder, parser):
        self._parser = parser
        self._data_source_folder = data_source_folder

    def keys(self):
        """Return all the files that could be used."""
        return [file[:-4] for file in os.listdir(self._data_source_folder) if file.lower().endswith(".ics")]

    def __getattr__(self, attribute):
        """Parse a file and return the result stored in the attribute."""
        source_file = attribute.replace('-', '_') + '.ics'
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

    def __getitem__(self, key):
        return getattr(self, key)

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


@pytest.fixture(params=[
    (data, key)
    for data in [CALENDARS, TIMEZONES, EVENTS]
    for key in data.keys() if key not in
    ( # exclude broken calendars here
        "big_bad_calendar", "issue_104_broken_calendar", "small_bad_calendar",
        "multiple_calendar_components", "pr_480_summary_with_colon"
    )
])
def ics_file(request):
    """An example ICS file."""
    data, key = request.param
    print(key)
    return data[key]
