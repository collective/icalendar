'''Issue #27 - multiple periods

   https://github.com/collective/icalendar/issues/27
'''
from icalendar import Calendar

def test_issue_27_multiple_periods(calendars):
    free_busy = list(calendars.issue_27_multiple_periods.walk('VFREEBUSY'))
    assert len(free_busy) == 1
    
    
