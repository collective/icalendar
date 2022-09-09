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
