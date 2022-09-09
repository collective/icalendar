'''Issue #168 - Parsing invalid icalendars fails without any warning

   https://github.com/collective/icalendar/issues/168
'''
from icalendar import Calendar

def test_issue_168_parsing_inavlid_calendars_no_warning(calendars):
    assert calendars.issue_168_input.to_ical() == calendars.issue_168_expected_output.raw_ics
