from icalendar.error import ICalParsingError, InvalidCalendar


def test_ical_parsing_error_is_invalid_calendar():
    assert issubclass(ICalParsingError, InvalidCalendar)


def test_ical_parsing_error_stores_attributes():
    error = ICalParsingError(
        message="Invalid property",
        line="SUMMARY:Meeting",
        line_number=42,
        value="SUMMARY:Meeting",
    )

    assert error.message == "Invalid property"
    assert error.line == "SUMMARY:Meeting"
    assert error.line_number == 42
    assert error.value == "SUMMARY:Meeting"
