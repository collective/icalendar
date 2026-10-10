"""Test the calendar specifically."""

from io import BytesIO

from icalendar.cal.calendar import Calendar

XML_HEADER = b'<?xml version="1.0" encoding="UTF-8"?>'
ICALENDAR_STREAM = b'<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">'


def test_calendar_bytes_start_with_xml_heading():
    """Test the calendar specifically."""
    xml = Calendar().to_xcal()
    assert xml.startswith(XML_HEADER)


def test_calendar_is_in_icalendar_stream():
    """Test the calendar specifically."""
    xml = Calendar().to_xcal()
    data = xml[len(XML_HEADER) :].lstrip()
    print(data)
    assert data.startswith(ICALENDAR_STREAM)


def test_can_write_to_file():
    """We can directly write to a file."""
    file = BytesIO()
    Calendar().to_xcal(file)
    assert file.getvalue().startswith(XML_HEADER)
