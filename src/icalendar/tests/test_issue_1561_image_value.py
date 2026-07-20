import pytest
import icalendar

def test_image_value_parameter_determines_type():
    """
    Test that the IMAGE property parses to the correct type depending
    on its VALUE parameter (if provided). See issue 1561.
    """
    for line, expected_type_name in [
        ("IMAGE;VALUE=URI:https://example.com/a.png", "vUri"),
        ("IMAGE;VALUE=BINARY:AAAA", "vBinary"),
        ("IMAGE:https://example.com/a.png", "vUnknown"),
    ]:
        ics = f"BEGIN:VEVENT\r\nUID:1\r\n{line}\r\nEND:VEVENT\r\n"
        ev = icalendar.Component.from_ical(ics)
        assert type(ev["IMAGE"]).__name__ == expected_type_name
