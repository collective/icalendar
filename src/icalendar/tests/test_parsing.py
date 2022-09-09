from icalendar import Event

from datetime import datetime

def test_no_tzid_when_utc_issue_58(events, utc):
    '''Issue #58 - TZID on UTC DATE-TIMEs

    https://github.com/collective/icalendar/issues/58
    '''
    # According to RFC 2445: "The TZID property parameter MUST NOT be
    # applied to DATE-TIME or TIME properties whose time values are
    # specified in UTC.
    date = datetime(2012, 7, 16, 0, 0, 0, tzinfo=utc)
    event = Event()
    event.add('dtstart', date)
    assert event.to_ical() == events.issue_58_expected_output.raw_ics

