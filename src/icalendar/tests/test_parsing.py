import pytest

from icalendar import vBinary

@pytest.mark.parametrize('timezone_info', [
    # General timezone aware dates in ical string
    (b'DTSTART;TZID=America/New_York:20130907T120000'),
    (b'DTEND;TZID=America/New_York:20130907T170000'),
    # Specific timezone aware exdates in ical string
    (b'EXDATE;TZID=America/New_York:20131012T120000'),
    (b'EXDATE;TZID=America/New_York:20131011T120000')
])
def test_timezone_info_present_in_ical_issue_112(events, timezone_info):
    '''Issue #112 - No timezone info on EXDATE

    https://github.com/collective/icalendar/issues/112
    '''
    timezone_info in events.issue_112_missing_tzinfo_on_exdate.to_ical()

def test_timezone_name_parsed_issue_112(events):
    '''Issue #112 - No timezone info on EXDATE

    https://github.com/collective/icalendar/issues/112
    '''
    assert events.issue_112_missing_tzinfo_on_exdate['exdate'][0].dts[0].dt.tzname() == 'EDT'

