import os
import logging

import pytest
import icalendar

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
                    source = parser(f.read())
                    setattr(self, attribute_name, source)
                except ValueError as error:
                    LOGGER.error(f'Could not load {source_file} due to {error}')

HERE = os.path.dirname(__file__)
TIMEZONES_FOLDER = os.path.join(HERE, 'timezones')
EVENTS_FOLDER = os.path.join(HERE, 'events')

TIMEZONES = DataSource(TIMEZONES_FOLDER, icalendar.Timezone.from_ical)
EVENTS = DataSource(EVENTS_FOLDER, icalendar.Event.from_ical)

@pytest.fixture
def timezones():
    return TIMEZONES

@pytest.fixture
def events():
    return EVENTS

