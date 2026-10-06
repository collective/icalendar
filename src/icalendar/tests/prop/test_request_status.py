"""Request status is text but with some extra functionality."""

import pytest

from icalendar import Event, vRequestStatus, vText
from icalendar.error import InvalidCalendar, JCalParsingError


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


@pytest.mark.parametrize(
    ("text", "code", "description"),
    [
        # special cases that should not crash but make no sense
        ("3.30.3", (), ""),
        ("3;", (), ""),
        ("10.", (), ""),
        ("", (), ""),
    ],
)
def test_special_cases(text, code, description):
    """These are invalid syntax cases. They should not crash."""
    request_status = vRequestStatus(text)
    assert request_status.code == code
    assert request_status.description == description
    assert request_status.data is None


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
    round_tripped_request_status = request_status.from_jcal(jcal)
    assert request_status == round_tripped_request_status


def test_adding_a_request_status():
    """Adding a request status should use the corrrect type."""
    e = Event()
    e.add("REQUEST-STATUS", "2.0;Success")
    assert e["REQUEST-STATUS"].code == (2, 0)
    assert e["REQUEST-STATUS"].description == "Success"


def test_invalid_request_status_does_not_error():
    """When the request status is invalid, accessors should not error."""
    r = vRequestStatus("invalid")
    assert r.code == ()
    assert r.description == ""
    assert r.data is None


def test_invalid_request_status_does_not_error_with_dots():
    """When the request status is invalid, accessors should not error."""
    r = vRequestStatus(".")
    assert r.code == ()
    assert r.description == ""
    assert r.data is None


def test_invalid_request_status_does_not_error_with_code():
    """When the request status is invalid, accessors should not error."""
    r = vRequestStatus(".3")
    assert r.code == ()
    assert r.description == ""
    assert r.data is None


def test_jcal_invaild_request_status():
    """The request status can have an unexpected length.

    See https://github.com/collective/icalendar/pull/1792#discussion_r4040271630
    """
    r = vRequestStatus.from_jcal(
        ["request-status", {}, "text", ["2.0", "Success", "data1", "data2"]]
    )
    assert r.code == (2, 0)
    assert r.description == "Success"
    assert r.data == "data1;data2"


@pytest.mark.parametrize("index", [0, 1, 2, 3])
@pytest.mark.parametrize("wrong_data", [0, None, 1.2])
def test_jcal_typing_of_request_status_content(index, wrong_data):
    """The request status is a text."""
    status_list = ["2.0", "Success", "data1", "data2"]
    status_list[index] = wrong_data
    with pytest.raises(JCalParsingError) as error:
        vRequestStatus.from_jcal(["request-status", {}, "text", status_list])
    assert "Each item in the list must be a string." in str(error.value)
    assert error.value.parser == "vRequestStatus"
    assert error.value.path == [3, index]


@pytest.mark.parametrize("length", [0, 1])
def test_jcal_too_short(length):
    """The request status is a text."""
    status_list = ["2.0"][:length]
    r = vRequestStatus.from_jcal(["request-status", {}, "text", status_list])
    assert r.code == ((2, 0) if length == 1 else ())
    assert r.description == ""
    assert r.data is None


@pytest.mark.parametrize(
    "code",
    ["2.0.0.0", ".0.0", "0.", "10.0", (2, 0, 11), (10, 2), (), (1, 1, 1, 1), (-1, 0)],
)
def test_request_status_new_rejects_invalid_code(code):
    """You are not allows to create invalid request status."""
    with pytest.raises(InvalidCalendar) as exc_info:
        vRequestStatus.new(code)
    message = exc_info.value.args[0]
    assert message == f"code must have 2 or 3 numbers from 0 to 9. Got {code!r}"


@pytest.mark.parametrize("code", ["2.0.0.0", ".0.0", "0.", "10.0", ""])
def test_disable_validation_for_jcal(code):
    """You are not allows to create invalid request status."""
    _ = vRequestStatus.new(code, validate=False)


@pytest.mark.parametrize("code", [None, [], 10, ("asd", 1)])
def test_type_error_on_invalid_type(code):
    with pytest.raises(TypeError):
        vRequestStatus.new(code)


@pytest.mark.parametrize("description", [None, [], 10, ("asd", 1)])
def test_invalid_description_type(description):
    with pytest.raises(TypeError):
        vRequestStatus.new("2.0", description)


@pytest.mark.parametrize("data", [[], 10, ("asd", 1)])
def test_invalid_data_type(data):
    with pytest.raises(TypeError):
        vRequestStatus.new("2.0", data=data)
