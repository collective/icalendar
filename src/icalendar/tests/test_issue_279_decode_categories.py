"""Make sure we can decode categories.

See https://github.com/collective/icalendar/issues/279
"""

from icalendar import Event


def test_no_category():
    """If no category is present, we would like to get a list."""
    event = Event()
    assert event.decoded("CATEGOIES", []) == []


def test_one_category(calendars):
    """One category should be in the list."""
    event = calendars.issue_322_expected_calendar.events[0]
    assert event.decoded("CATEGORIES", []) == ["Lecture"]


def test_several_categories(calendars):
    """Several categories are comma separated."""
    event = calendars.issue_279_decode_categories.events[0]
    assert event.decoded("CATEGORIES", []) == ["Lecture", "University"]
