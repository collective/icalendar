'''Tests checking that parsing works'''
import pytest
from icalendar import Calendar
from icalendar import vRecur

@pytest.mark.parametrize('event_name', [
    # https://github.com/collective/icalendar/pull/100
    ('issue_100_transformed_doctests_into_unittests'),
    ('issue_184_broken_representation_of_period'),
])
def test_event_to_ical_is_inverse_of_from_ical(events, event_name):
    event = getattr(events, event_name)
    assert event.to_ical() == event.raw_ics

def test_decode_rrule_attribute_error_issue_70(events):
    # Issue #70 - e.decode("RRULE") causes Attribute Error
    # see https://github.com/collective/icalendar/issues/70
    recur = events.issue_70_rrule_causes_attribute_error.decoded('RRULE')
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b'FREQ=WEEKLY;UNTIL=20070619T225959;INTERVAL=1'

def test_description_parsed_properly_issue_53(events):
    '''Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    '''
    assert b'July 12 at 6:30 PM' in events.issue_53_description_parsed_properly['DESCRIPTION'].to_ical()

def test_raises_value_error_for_properties_without_parent_pull_179():
        '''Found an issue where from_ical() would raise IndexError for
        properties without parent components.

        https://github.com/collective/icalendar/pull/179
        '''
        with pytest.raises(ValueError):
            Calendar.from_ical('VERSION:2.0')

def test_tzid_parsed_properly_issue_53(timezones):
    '''Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    '''
    assert timezones.issue_53_tzid_parsed_properly['tzid'].to_ical() == b'America/New_York'
    
def test_timezones_to_ical_is_inverse_of_from_ical(timezones):
    '''Issue #55 - Parse error on utc-offset with seconds value
     see https://github.com/collective/icalendar/issues/55'''
    timezone = timezones['issue_55_parse_error_on_utc_offset_with_seconds']
    assert timezone.to_ical() == timezone.raw_ics
