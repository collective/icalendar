import pytest

from icalendar import Event

from datetime import datetime

@pytest.mark.parametrize('date, expected_output', [
    (datetime(2012, 7, 16, 0, 0, 0), b'DTSTART;VALUE=DATE-TIME:20120716T000000Z'),
    (datetime(2021, 11, 17, 15, 9, 15), b'DTSTART;VALUE=DATE-TIME:20211117T150915Z')
])
def test_no_tzid_when_utc(utc, date, expected_output):
    '''Issue #58  - TZID on UTC DATE-TIMEs
       Issue #335 - UTC timezone identification is broken

    https://github.com/collective/icalendar/issues/58
    https://github.com/collective/icalendar/issues/335
    '''
    # According to RFC 2445: "The TZID property parameter MUST NOT be
    # applied to DATE-TIME or TIME properties whose time values are
    # specified in UTC.
    date = date.replace(tzinfo=utc)
    event = Event()
    event.add('dtstart', date)
    assert expected_output in event.to_ical()

