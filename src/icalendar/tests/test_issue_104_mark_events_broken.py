import os
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

def test_dont_ignore_exceptions_on_broken_calendars_issue_104(calendars_folder):
    '''Issue #104 - line parsing error in a VCALENDAR
    (which doesn't have ignore_exceptions). Should raise an exception.
    '''
    calendar_path = os.path.join(calendars_folder, 'issue_104_broken_calendar.ics')
    with pytest.raises(ValueError), open(calendar_path) as f:
        Calendar.from_ical(f.read())
