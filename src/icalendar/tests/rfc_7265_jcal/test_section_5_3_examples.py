"""Check that we convert the examples propertly."""

from typing import TYPE_CHECKING

from icalendar.parser_tools import to_unicode

if TYPE_CHECKING:
    from icalendar import Calendar


def test_convert_coffee(calendars):
    """convert the unknown value property"""
    calendar = calendars.rfc_7265_example_2
    ical = calendar.to_ical().decode()
    print(to_unicode(ical))
    assert r"X-COFFEE-DATA:Stenophylla\;Guinea\\\,Africa" in ical


def test_conversion_from_ical(calendars):
    """Convert the example to jCal."""
    calendar: Calendar = calendars.rfc_7265_example_1
    jcal = calendar.to_jcal()
    assert jcal[1][0] == ["x-complaint-deadline", {}, "unknown", "20110512T120000Z"]


def test_example_3(calendars):
    """Test the 3rd example."""
    calendar = calendars.rfc_7265_example_3
    ical = calendar.to_ical().decode()
    assert "PERCENT-COMPLETE:95" in ical


def test_example_4(events):
    """Test the 4th example."""
    event = events.rfc_7265_example_4
    ical = event.to_jcal()
    assert ical[1][0] == ["dtstart", {"x-slack": "30.3"}, "date", "2011-05-12"]
