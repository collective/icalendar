import pytz
import pytest
from datetime import datetime
from dateutil import tz
try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

from icalendar import Event

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

