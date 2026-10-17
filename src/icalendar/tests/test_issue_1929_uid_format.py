"""The UID setter validates the value as RFC 5545 ``text``.

See https://github.com/collective/icalendar/issues/1929
"""

from uuid import uuid4

import pytest

from icalendar import Calendar, Event, Journal, Todo
from icalendar.error import InvalidCalendar

COMPONENTS = [Calendar, Event, Journal, Todo]


@pytest.mark.parametrize("cls", COMPONENTS)
@pytest.mark.parametrize(
    "value",
    [
        "1234",
        "AbC-123",
        "d755cef5-2311-46ed-a0e1-6733c9e15c63",
        str(uuid4()),
        # The common local@domain form, e.g. from RFC 9253, must stay valid.
        "19960401-080045-4000F192713-0052@example.com",
        "event-1@example.com",
        "19960401-080045-4000F192713.ics",
        "café-123",  # arbitrary unicode text is allowed
        "with\ttab",  # TAB is WSP and allowed in RFC 5545 text
        "a",
        "a" * 300,  # RFC 5545 requires persisting values of at least 255 octets
    ],
)
def test_valid_uid_is_accepted_unchanged(cls, value):
    """A valid ``text`` value is accepted and stored verbatim (casing kept)."""
    component = cls()
    component.uid = value
    assert component.uid == value


@pytest.mark.parametrize("cls", COMPONENTS)
def test_uuid_object_is_accepted(cls):
    """A :class:`uuid.UUID` object serializes to a valid UID."""
    value = uuid4()
    component = cls()
    component.uid = value
    assert component.uid == str(value)


@pytest.mark.parametrize("cls", COMPONENTS)
@pytest.mark.parametrize(
    "value",
    [
        "",  # empty is not a usable identifier
        "line1\r\nline2",  # CR/LF would break serialization
        "null\x00byte",
        "bell\x07",
        "delete\x7f",
    ],
)
def test_invalid_uid_is_rejected(cls, value):
    """A value that cannot be serialized raises :exc:`InvalidCalendar`."""
    component = cls()
    with pytest.raises(InvalidCalendar):
        component.uid = value


@pytest.mark.parametrize("cls", COMPONENTS)
def test_rejected_uid_does_not_overwrite_existing_value(cls):
    """A failed set leaves any previously-set, valid UID untouched."""
    component = cls()
    component.uid = "valid-123"
    with pytest.raises(InvalidCalendar):
        component.uid = "bad\r\nvalue"
    assert component.uid == "valid-123"


@pytest.mark.parametrize("cls", COMPONENTS)
def test_setting_uid_to_none_deletes_it(cls):
    """Setting the UID to ``None`` clears it without validating."""
    component = cls()
    component.uid = "valid-123"
    component.uid = None
    assert component.uid == ""
