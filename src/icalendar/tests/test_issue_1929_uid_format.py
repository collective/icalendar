"""The UID setter validates the value as RFC 5545 ``text``.

See https://github.com/collective/icalendar/issues/1929
"""

from uuid import uuid4

import pytest

from icalendar import Calendar, Event, Journal, Todo
from icalendar.error import InvalidCalendar


@pytest.fixture(params=[Calendar, Event, Journal, Todo])
def cls(request):
    """Return a component class that supports the UID property."""
    return request.param


@pytest.mark.parametrize(
    "value",
    [
        "1234",
        "AbC-123",  # mixed case is preserved, not normalised
        "d755cef5-2311-46ed-a0e1-6733c9e15c63",  # a UUID is a valid token
        str(uuid4()),
        "a",
        "-",  # a lone hyphen is a valid token character
        "a" * 254,  # 254 octets is allowed; 255 or more is not
    ],
)
def test_valid_uid_is_accepted_unchanged(cls, value):
    """A valid ``text`` value is accepted and stored verbatim (casing kept)."""
    component = cls()
    component.uid = value
    assert component.uid == value


def test_uuid_object_is_accepted(cls):
    """A :class:`uuid.UUID` object serializes to a valid UID."""
    value = uuid4()
    component = cls()
    component.uid = value
    assert component.uid == str(value)


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


def test_rejected_uid_does_not_overwrite_existing_value(cls):
    """A failed set leaves any previously-set, valid UID untouched."""
    component = cls()
    component.uid = "valid-123"
    with pytest.raises(InvalidCalendar):
        component.uid = "bad\r\nvalue"
    assert component.uid == "valid-123"


def test_setting_uid_to_none_deletes_it(cls):
    """Setting the UID to ``None`` clears it without validating."""
    component = cls()
    component.uid = "valid-123"
    component.uid = None
    assert component.uid == ""


@pytest.mark.parametrize("value", [object(), 123, 1.5, ["a"], {"a": 1}])
def test_uid_wrong_type_raises_type_error(cls, value):
    """Setting the UID to a non-string, non-UUID value raises TypeError."""
    component = cls()
    with pytest.raises(TypeError):
        component.uid = value
