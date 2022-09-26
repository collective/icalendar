'''Tests checking that parsing works'''
from icalendar import vRecur

def test_decode_rrule_attribute_error_issue_70(events):
    # Issue #70 - e.decode("RRULE") causes Attribute Error
    # see https://github.com/collective/icalendar/issues/70
    recur = events.issue_70_rrule_causes_attribute_error.decoded('RRULE')
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b'FREQ=WEEKLY;UNTIL=20070619T225959;INTERVAL=1'

def test_description_parsed_properly_issue_53(events):
    '''Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    '''
    assert b'July 12 at 6:30 PM' in events.issue_53_description_parsed_properly['DESCRIPTION'].to_ical()

def test_tzid_parsed_properly_issue_53(timezones):
    '''Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    '''
    assert timezones.issue_53_tzid_parsed_properly['tzid'].to_ical() == b'America/New_York'
    
def test_timezones_to_ical_is_inverse_of_from_ical(timezones):
    '''Issue #55 - Parse error on utc-offset with seconds value
     see https://github.com/collective/icalendar/issues/55'''
    timezone = timezones['issue_55_parse_error_on_utc_offset_with_seconds']
    assert timezone.to_ical() == timezone.raw_ics
