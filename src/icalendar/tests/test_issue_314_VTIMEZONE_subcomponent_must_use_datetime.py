"""These tests make sure that Issue 314 can be closed.

See https://github.com/collective/icalendar/issues/314
"""

def test_datetime_in_event(calendars):
    """Check that the calendar can be parsed without an error."""
    calendars.issue_314_VTIMEZONE_subcomponent_must_use_datetime.to_ical()
