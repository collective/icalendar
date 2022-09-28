'''Tests checking that parsing works'''
import pytest
from icalendar import Calendar
from icalendar import vRecur
from icalendar import vBinary

@pytest.mark.parametrize('timezone_info', [
    # General timezone aware dates in ical string
    (b'DTSTART;TZID=America/New_York:20130907T120000'),
    (b'DTEND;TZID=America/New_York:20130907T170000'),
    # Specific timezone aware exdates in ical string
    (b'EXDATE;TZID=America/New_York:20131012T120000'),
    (b'EXDATE;TZID=America/New_York:20131011T120000')
])
def test_timezone_info_present_in_ical_issue_112(events, timezone_info):
    '''Issue #112 - No timezone info on EXDATE

    https://github.com/collective/icalendar/issues/112
    '''
    timezone_info in events.issue_112_missing_tzinfo_on_exdate.to_ical()

def test_timezone_name_parsed_issue_112(events):
    '''Issue #112 - No timezone info on EXDATE

    https://github.com/collective/icalendar/issues/112
    '''
    assert events.issue_112_missing_tzinfo_on_exdate['exdate'][0].dts[0].dt.tzname() == 'EDT'

def test_issue_157_removes_trailing_semicolon(events):
    '''Issue #157 - Recurring rules and trailing semicolons

    https://github.com/collective/icalendar/pull/157
    '''
    recur = events.issue_157_removes_trailing_semicolon.decoded("RRULE")
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b'FREQ=YEARLY;BYDAY=1SU;BYMONTH=11'

@pytest.mark.parametrize('event_name', [
    # https://github.com/collective/icalendar/pull/100
    ('issue_100_transformed_doctests_into_unittests'),
    ('issue_184_broken_representation_of_period'),
])
def test_event_to_ical_is_inverse_of_from_ical(events, event_name):
    """Make sure that an event's ICS is equal to the ICS it was made from."""
    event = events[event_name]
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
