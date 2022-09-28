import os
import logging

import pytest
import icalendar

LOGGER = logging.getLogger(__name__)

class DataSource:
    '''A collection of parsed ICS elements (e.g calendars, timezones, events)'''
    def __init__(self, data_source_folder, parser):
        self._parser = parser
        self._data_source_folder = data_source_folder

    def __getattr__(self, attribute):
        if not attribute in self.__dict__:
            source_file = attribute.replace('-', '_') + '.ics'
            source_path = os.path.join(self.__dict__['_data_source_folder'], source_file)
            with open(source_path, 'rb') as f:
                try:
                    raw_ics = f.read()
                    source = self.__dict__['_parser'](raw_ics)
                    source.raw_ics = raw_ics
                    self.__dict__[attribute] = source
                except ValueError as error:
                    LOGGER.error(f'Could not load {source_file} due to {error}')
        return self.__dict__[attribute]

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return repr(self.__dict__)

HERE = os.path.dirname(__file__)
TIMEZONES_FOLDER = os.path.join(HERE, 'timezones')
EVENTS_FOLDER = os.path.join(HERE, 'events')
CALENDARS_FOLDER = os.path.join(HERE, 'calendars')

@pytest.fixture
def timezones():
    return DataSource(TIMEZONES_FOLDER, icalendar.Timezone.from_ical)

@pytest.fixture
def events():
    return DataSource(EVENTS_FOLDER, icalendar.Event.from_ical)

@pytest.fixture
def calendar_file(request):
    print(request.param)
    return os.path.join(CALENDARS_FOLDER, request.param)

