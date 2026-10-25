"""Explain how to set values that jCal and xCal can serialize (issue 1983)."""

import pytest

from icalendar import Calendar, Event, vText


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
@pytest.mark.parametrize(
    "value", ["Meeting", b"Meeting", 42, [vText("First"), "Second"]]
)
def test_raw_values_raise_a_helpful_error(format_name, value):
    """Name the invalid property and direct callers to add()."""
    event = Event()
    event["SUMMARY"] = value
    with pytest.raises(TypeError, match=r"SUMMARY.*add\(\)"):
        getattr(event, f"to_{format_name}")()


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
def test_nested_raw_values_raise_a_helpful_error(format_name):
    """The same guidance applies to values in subcomponents."""
    calendar = Calendar()
    event = Event()
    event["SUMMARY"] = "Meeting"
    calendar.add_component(event)
    with pytest.raises(TypeError, match=r"SUMMARY.*add\(\)"):
        getattr(calendar, f"to_{format_name}")()


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
def test_add_produces_serializable_values(format_name):
    """The recommended setter converts raw strings to property values."""
    event = Event()
    event.add("SUMMARY", "Meeting")
    assert getattr(event, f"to_{format_name}")()


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
def test_serializer_attribute_errors_are_preserved(format_name):
    """Errors inside a custom serializer must not be mistaken for raw values."""

    class BrokenText(vText):
        def to_jcal(self, _name):
            raise AttributeError("custom serializer failed")

        def to_xcal(self, _element):
            raise AttributeError("custom serializer failed")

    event = Event()
    event["SUMMARY"] = BrokenText("Meeting")
    with pytest.raises(AttributeError, match="custom serializer failed"):
        getattr(event, f"to_{format_name}")()
