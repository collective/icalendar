"""Tests for https://github.com/collective/icalendar/issues/1593."""

from icalendar import Event, vCalAddress


def test_mixed_attendees_normalizes_only_the_string_slot():
    """Normalize a string without replacing the list or existing address."""
    existing = vCalAddress("mailto:existing@example.com")
    existing.params["CN"] = "Existing User"
    attendees = ["first@example.com", existing]
    e = Event()
    e.attendees = attendees

    assert e.attendees is attendees
    assert e.attendees[1] is existing
    assert e.attendees[1].params["CN"] == "Existing User"
    assert isinstance(e.attendees[0], vCalAddress)
    assert str(e.attendees[0]) == "mailto:first@example.com"
