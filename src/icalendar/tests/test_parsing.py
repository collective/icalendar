import pytz
import pytest
import base64
from datetime import datetime
from dateutil import tz
try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

from icalendar import Event, vBinary, Calendar

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
def test_no_tzid_when_utc_issue_58(events, timezone):
    '''Issue #58 - TZID on UTC DATE-TIMEs

    https://github.com/collective/icalendar/issues/58
    '''
    # According to RFC 2445: "The TZID property parameter MUST NOT be
    # applied to DATE-TIME or TIME properties whose time values are
    # specified in UTC.
    date = datetime(2012, 7, 16, 0, 0, 0)
    event = Event()
    event.add('dtstart', date.astimezone(timezone))
    assert event.to_ical() == events.issue_58_expected_output.raw_ics

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

