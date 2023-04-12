"""These are tests for Issue #348

see https://github.com/collective/icalendar/issues/348
"""

def test_calendar_can_be_parsed_correctly(calendars):
    """Exception when there's no ':' when parsing value #348

    see https://github.com/collective/icalendar/issues/348 
    """
    freebusy = calendars.issue_348_exception_parsing_value.walk("VFREEBUSY")[0]
    assert freebusy["ORGANIZER"].params["CN"] == "Sixt SE"
