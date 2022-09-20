import pytest
from icalendar import Calendar

def test_raises_value_error_for_properties_without_parent_pull_179():
        '''Found an issue where from_ical() would raise IndexError for
        properties without parent components.

        https://github.com/collective/icalendar/pull/179
        '''
        with pytest.raises(ValueError):
            Calendar.from_ical('VERSION:2.0')

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
