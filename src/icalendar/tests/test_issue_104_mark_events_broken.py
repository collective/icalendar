import pytest

from icalendar import Event, Calendar

def test_ignore_exceptions_on_broken_events_issue_104(events):
    ''' Issue #104 - line parsing error in a VEVENT
    (which has ignore_exceptions). Should mark the event broken
    but not raise an exception.

    https://github.com/collective/icalendar/issues/104
    '''
    assert events.issue_104_mark_events_broken.is_broken # TODO: REMOVE FOR NEXT MAJOR RELEASE
    assert events.issue_104_mark_events_broken.errors == [(None, "Content line could not be parsed into parts: 'X': Invalid content line")]

def test_dont_ignore_exceptions_on_broken_calendars_issue_104(calendars):
    '''Issue #104 - line parsing error in a VCALENDAR
    (which doesn't have ignore_exceptions). Should raise an exception.
    '''
    with pytest.raises(ValueError):
        calendars.issue_104_broken_calendar
