"""Request status is text but with some extra functionality."""

import pytest

from icalendar import Event, vRequestStatus, vText


def test_request_status_is_text():
    """Make sure we inherit the information.

    This is important as we do not want to break the API interface.
    """
    assert issubclass(vRequestStatus, vText)
    assert vRequestStatus.default_value == "TEXT"


mark_examples = pytest.mark.parametrize(
    ("text", "code", "description", "data", "text_serialized"),
    [
        ("2.0;Success", (2, 0), "Success", None, None),
        (
            "3.1;Invalid property value;DTSTART:96-Apr-01",
            (3, 1),
            "Invalid property value",
            "DTSTART:96-Apr-01",
            None,
        ),
        (
            r"2.8; Success\, repeating event ignored. Scheduled as a single event.;RRULE:FREQ=WEEKLY\;INTERVAL=2",
            (2, 8),
            " Success, repeating event ignored. Scheduled as a single event.",
            "RRULE:FREQ=WEEKLY;INTERVAL=2",
            None,
        ),
        (
            "4.1;Event conflict.  Date-time is busy.",
            (4, 1),
            "Event conflict.  Date-time is busy.",
            None,
            None,
        ),
        (
            "3.7;Invalid calendar user;ATTENDEE:mailto:jsmith@example.com",
            (3, 7),
            "Invalid calendar user",
            "ATTENDEE:mailto:jsmith@example.com",
            None,
        ),
        # special cases that should not crash but make no sense
        ("3.3", (3, 3), "", None, "3.3;"),
        ("3", (3,), "", None, "3;"),
        ("10.", (10,), "", None, "10;"),
        ("", (), "", None, ";"),
        (
            r"1.2;escape\;semicolon;data\;escape",
            (1, 2),
            "escape;semicolon",
            "data;escape",
            None,
        ),
    ],
)


@mark_examples
def test_parse_content(text, code, description, data, text_serialized):
    """Test parsing the REQUEST-STATUS base on the icalendar data."""
    request_status = vRequestStatus(text)
    assert request_status.code == code
    assert request_status.description == description
    assert request_status.data == data


def test_from_ical(events):
    """Test the presence in the parsed calendar."""
    event: Event = events.rfc_7265_request_status

    # 2.0;Success
    assert event.REQUEST_STATUS[0].code == (2, 0)
    assert event.REQUEST_STATUS[0].description == "Success"
    assert event.REQUEST_STATUS[0].data is None

    # 3.7;Invalid calendar user;ATTENDEE:mailto:jsmith@example.org
    assert event.REQUEST_STATUS[1].code == (3, 7)
    assert event.REQUEST_STATUS[1].description == "Invalid calendar user"
    assert event.REQUEST_STATUS[1].data == "ATTENDEE:mailto:jsmith@example.org"


def test_new_without_data():
    """Test a simple creation."""
    request_status = vRequestStatus.new((2, 0), "Success")
    assert request_status.code == (2, 0)
    assert request_status.description == "Success"
    assert request_status.data is None


@mark_examples
def test_create_content(text, code, description, data, text_serialized):
    """Test creating a request status with new()"""
    request_status = vRequestStatus.new(code, description, data)
    text_serialized = text if text_serialized is None else text_serialized
    assert request_status.code == code
    assert request_status.description == description
    assert request_status.data == data
    assert request_status == text_serialized


def test_create_special_cases():
    """Test creating a request status with new()"""
    request_status = vRequestStatus.new(3)
    assert request_status.code == (3,)
    assert request_status.description == ""
    assert request_status.data is None
    assert request_status == "3;"

    request_status = vRequestStatus.new("3.4")
    assert request_status.code == (3, 4)
    assert request_status.description == ""
    assert request_status.data is None
    assert request_status == "3.4;"


@mark_examples
def test_from_jcal(text, code, description, data, text_serialized):
    """Check that jcal round trip preserves semicolon escape."""
    request_status = vRequestStatus.new(code, description, data)
    jcal = request_status.to_jcal("request-status")
    print(jcal)
    round_tripped_request_status = request_status.from_jcal(jcal)
    assert request_status == round_tripped_request_status
