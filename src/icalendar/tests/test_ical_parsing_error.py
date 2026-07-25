from icalendar.error import ICalParsingError, InvalidCalendar


def test_ical_parsing_error_is_invalid_calendar():
    assert issubclass(ICalParsingError, InvalidCalendar)


def test_ical_parsing_error_stores_attributes():
    error = ICalParsingError(
        message="Invalid property",
        line="SUMMARY:Meeting",
        line_number=42,
        value={"property": "SUMMARY"},
    )

    assert error.message == "Invalid property"
    assert error.line == "SUMMARY:Meeting"
    assert error.line_number == 42
    assert error.value == {"property": "SUMMARY"}


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
        {"property": "SUMMARY"},
    )

    assert error.message == "Invalid property"
    assert error.line == "SUMMARY:Meeting"
    assert error.line_number == 42
    assert error.value == {"property": "SUMMARY"}


def test_ical_parsing_error_message_only():
    error = ICalParsingError("Malformed date")

    assert str(error) == "Malformed date"


def test_ical_parsing_error_message_with_value():
    error = ICalParsingError(
        "Malformed date",
        value="20240399",
    )

    assert str(error) == "Malformed date: '20240399'"


def test_ical_parsing_error_message_with_line():
    error = ICalParsingError(
        "Malformed date",
        line="DTSTART:20240399",
    )

    assert str(error) == "Malformed date ('DTSTART:20240399')"


def test_ical_parsing_error_message_with_line_number():
    error = ICalParsingError(
        "Malformed date",
        line_number=42,
    )

    assert str(error) == "Malformed date (line 42)"


def test_ical_parsing_error_message_with_line_and_line_number():
    error = ICalParsingError(
        "Malformed date",
        line="DTSTART:20240399",
        line_number=42,
    )

    assert str(error) == "Malformed date (line 42: 'DTSTART:20240399')"


def test_ical_parsing_error_message_with_all_context():
    error = ICalParsingError(
        "Malformed date",
        line="DTSTART:20240399",
        line_number=42,
        value="20240399",
    )

    assert str(error) == "Malformed date: '20240399' (line 42: 'DTSTART:20240399')"
