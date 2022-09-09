'''Tests checking that parsing works'''
import pytz
import pytest
import base64
from datetime import datetime
from dateutil import tz
try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

from icalendar import Event, vBinary, Calendar, vRecur
from icalendar.parser import Contentline, Parameters

def test_description_parsed_properly_issue_53(events):
    '''Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    '''
    assert b'July 12 at 6:30 PM' in events.issue_53_description_parsed_properly['DESCRIPTION'].to_ical()

def test_tzid_parsed_properly_issue_53(timezones):
    '''Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    '''
    assert timezones.issue_53_tzid_parsed_properly['tzid'].to_ical() == b'America/New_York'

@pytest.mark.parametrize('timezone', [
    pytz.utc,
    zoneinfo.ZoneInfo('UTC'),
    pytz.timezone('UTC'),
    tz.UTC,
    tz.gettz('UTC')])
@pytest.mark.parametrize('date, expected_output', [
    (datetime(2012, 7, 16, 0, 0, 0), b'DTSTART;VALUE=DATE-TIME:20120716T000000Z'),
    (datetime(2021, 11, 17, 15, 9, 15), b'DTSTART;VALUE=DATE-TIME:20211117T150915Z')
])
def test_no_tzid_when_utc(timezone, date, expected_output):
    '''Issue #58  - TZID on UTC DATE-TIMEs
       Issue #335 - UTC timezone identification is broken

    https://github.com/collective/icalendar/issues/58
    https://github.com/collective/icalendar/issues/335
    '''
    # According to RFC 2445: "The TZID property parameter MUST NOT be
    # applied to DATE-TIME or TIME properties whose time values are
    # specified in UTC.
    date = date.replace(tzinfo=timezone)
    event = Event()
    event.add('dtstart', date.astimezone(timezone))
    assert expected_output in event.to_ical()

def test_vBinary_base64_encoded_issue_82():
    '''Issue #82 - vBinary __repr__ called rather than to_ical from
                   container types
    https://github.com/collective/icalendar/issues/82
    '''
    b = vBinary('text')
    b.params['FMTTYPE'] = 'text/plain'
    assert b.to_ical() == base64.b64encode(b'text')

def test_creates_event_with_base64_encoded_attachment_issue_82(events):
    '''Issue #82 - vBinary __repr__ called rather than to_ical from
                   container types
    https://github.com/collective/icalendar/issues/82
    '''
    b = vBinary('text')
    b.params['FMTTYPE'] = 'text/plain'
    event = Event()
    event.add('ATTACH', b)
    assert event.to_ical() == events.issue_82_expected_output.raw_ics

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

def test_raises_value_error_for_properties_without_parent_pull_179():
        '''Found an issue where from_ical() would raise IndexError for
        properties without parent components.

        https://github.com/collective/icalendar/pull/179
        '''
        with pytest.raises(ValueError):
            Calendar.from_ical('VERSION:2.0')

@pytest.mark.parametrize('raw_content_line, expected_output', [
    # Issue #142 - Multivalued parameters. This is needed for VCard 3.0.
    # see https://github.com/collective/icalendar/pull/142
    ('TEL;TYPE=HOME,VOICE:000000000', ('TEL', Parameters({'TYPE': ['HOME', 'VOICE']}), '000000000')),
    # Issue #143 - Allow dots in property names. Another vCard related issue.
    # see https://github.com/collective/icalendar/pull/143
    ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR:;;This is the Adress 08; Some City;;12345;Germany', ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR', Parameters(), ';;This is the Adress 08; Some City;;12345;Germany'))
])
def test_content_lines_parsed_properly(raw_content_line, expected_output):
    assert Contentline.from_ical(raw_content_line).parts() == expected_output

def test_issue_157_removes_trailing_semicolon(events):
    '''Issue #157 - Recurring rules and trailing semicolons

    https://github.com/collective/icalendar/pull/157
    '''
    recur = events.issue_157_removes_trailing_semicolon.decoded("RRULE")
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b'FREQ=YEARLY;BYDAY=1SU;BYMONTH=11'

@pytest.mark.parametrize('calendar_name', [
    # Issue #178 - A component with an unknown/invalid name is represented
    # as one of the known components, the information about the original
    # component name is lost.
    # https://github.com/collective/icalendar/issues/178 https://github.com/collective/icalendar/pull/180
    # Parsing of a nonstandard component
    'issue_178_component_with_invalid_name_represented',
    # Nonstandard component inside other components, also has properties
    'issue_178_custom_component_inside_other',
    # Nonstandard component is able to contain other components
    'issue_178_custom_component_contains_other'])
def test_calendar_to_ical_is_inverse_of_from_ical(calendars, calendar_name):
    calendar = getattr(calendars, calendar_name)
    assert calendar.to_ical() == calendar.raw_ics

