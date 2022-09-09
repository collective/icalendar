'''Tests checking that parsing works'''
from icalendar import vRecur

def test_issue_157_removes_trailing_semicolon(events):
    '''Issue #157 - Recurring rules and trailing semicolons

    https://github.com/collective/icalendar/pull/157
    '''
    recur = events.issue_157_removes_trailing_semicolon.decoded("RRULE")
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b'FREQ=YEARLY;BYDAY=1SU;BYMONTH=11'

