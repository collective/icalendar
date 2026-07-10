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


def test_ical_parsing_error_required_parameters_only():
    error = ICalParsingError("Invalid property")

    assert error.message == "Invalid property"
    assert error.line is None
    assert error.line_number is None
    assert error.value is None


def test_ical_parsing_error_parameter_order():
    error = ICalParsingError(
        "Invalid property",
        "SUMMARY:Meeting",
        42,
        "SUMMARY:Meeting",
    )

    assert error.message == "Invalid property"
    assert error.line == "SUMMARY:Meeting"
    assert error.line_number == 42
    assert error.value == "SUMMARY:Meeting"
