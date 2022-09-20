'''Tests checking that parsing works'''
import pytest

@pytest.mark.parametrize('event_name', [
    # https://github.com/collective/icalendar/pull/100
    ('issue_100_transformed_doctests_into_unittests'),
    ('issue_184_broken_representation_of_period'),
])
def test_event_to_ical_is_inverse_of_from_ical(events, event_name):
    event = getattr(events, event_name)
    assert event.to_ical() == event.raw_ics

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
