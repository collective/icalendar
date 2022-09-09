'''Tests checking that parsing works'''

def test_timezones_to_ical_is_inverse_of_from_ical(timezones):
    '''Issue #55 - Parse error on utc-offset with seconds value
     see https://github.com/collective/icalendar/issues/55'''
    timezone = timezones['issue_55_parse_error_on_utc_offset_with_seconds']
    assert timezone.to_ical() == timezone.raw_ics

