"""
Test for GitHub issue #1257:
Replace print() in documentation
"""

from icalendar import Calendar
from icalendar.cal.event import Event
from icalendar.cal.component import Component


def test_view_returns_string():
    """view() should return a str, not bytes."""
    cal = Calendar()
    cal["summary"] = "Test"
    assert isinstance(cal.view(), str)

def test_view_no_crlf():
    """view() should use Unix line endings, not CRLF."""
    cal = Calendar()
    cal["summary"] = "Test"
    assert "\r\n" not in cal.view()

def test_view_starts_and_ends_correctly():
    """view() output should be stripped and bounded by BEGIN/END."""
    cal = Calendar()
    result = cal.view()
    assert result.startswith("BEGIN:VCALENDAR")
    assert result.endswith("END:VCALENDAR")

def test_view_contains_properties():
    """view() should include the component's properties."""
    cal = Calendar()
    cal["summary"] = "My Meeting"
    assert "SUMMARY:My Meeting" in cal.view()

def test_view_works_on_event():
    """view() should work on Event components too, not just Calendar."""
    event = Event()
    event["summary"] = "Standup"
    result = event.view()
    assert result.startswith("BEGIN:VEVENT")
    assert result.endswith("END:VEVENT")
    assert "SUMMARY:Standup" in result

def test_view_works_on_base_component():
    """view() should be available on the base Component class."""
    comp = Component()
    comp["key"] = "value"
    result = comp.view()
    assert isinstance(result, str)
    assert "KEY:value" in result

def test_view_consistent_with_to_ical():
    """view() should be the decoded, cleaned version of to_ical()."""
    cal = Calendar()
    cal["summary"] = "Consistency check"
    expected = cal.to_ical().decode("utf-8").replace("\r\n", "\n").strip()
    assert cal.view() == expected