import os
import logging

import pytest
import icalendar

import datetime
import pytz
from dateutil import tz
try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

LOGGER = logging.getLogger(__name__)

class DataSource:
    '''A collection of parsed ICS elements (e.g calendars, timezones, events)'''
    def __init__(self, data_source_folder, parser):
        for source_file in os.listdir(data_source_folder):
            source_path = os.path.join(data_source_folder, source_file)
            name = os.path.splitext(source_file)[0]
            attribute_name = name.replace('-', '_')
            with open(source_path, 'rb') as f:
                try:
                    raw_ics = f.read()
                    source = parser(raw_ics)
                    source.raw_ics = raw_ics
                    setattr(self, attribute_name, source)
                except ValueError as error:
                    LOGGER.error(f'Could not load {source_file} due to {error}')

HERE = os.path.dirname(__file__)
TIMEZONES_FOLDER = os.path.join(HERE, 'timezones')
EVENTS_FOLDER = os.path.join(HERE, 'events')
CALENDARS_FOLDER = os.path.join(HERE, 'calendars')

TIMEZONES = DataSource(TIMEZONES_FOLDER, icalendar.Timezone.from_ical)
EVENTS = DataSource(EVENTS_FOLDER, icalendar.Event.from_ical)
CALENDARS = DataSource(CALENDARS_FOLDER, icalendar.Calendar.from_ical)

@pytest.fixture
def timezones():
    return TIMEZONES

@pytest.fixture
def events():
    return EVENTS

@pytest.fixture
def calendars():
    return CALENDARS

@pytest.fixture
def calendars_folder():
    return CALENDARS_FOLDER

@pytest.fixture(params=[pytz.timezone, tz.gettz, zoneinfo.ZoneInfo])
def timezone(request):
    return request.param
