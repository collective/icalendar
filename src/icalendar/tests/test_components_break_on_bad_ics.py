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

def test_rdate_dosent_become_none_on_invalid_input_issue_464(events):
    '''Issue #464 - [BUG] RDATE can become None if value is invalid
    https://github.com/collective/icalendar/issues/464
    '''
    assert events.issue_464_invalid_rdate.is_broken
    assert ('RDATE', 'Expected period format, got: 199709T180000Z/PT5H30M') in events.issue_464_invalid_rdate.errors
    assert not b'RDATE:None' in events.issue_464_invalid_rdate.to_ical()

@pytest.mark.parametrize('calendar_name', [
    'big_bad_calendar',
    'small_bad_calendar',
    'multiple_calendar_components',
    'pr_480_summary_with_colon',
])
def test_error_message_doesnt_get_too_big(calendars, calendar_name):
    with pytest.raises(ValueError) as exception:
        calendars[calendar_name]
    # Ignore part before first : for the test.
    assert len(str(exception).split(': ', 1)[1]) <= 100

