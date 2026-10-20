"""Tests for issue #1929: Enforce UID format for setters.

See https://github.com/collective/icalendar/issues/1929
RFC 7986 Section 5.3: https://datatracker.ietf.org/doc/html/rfc7986.html#section-5.3
RFC 5545 Section 3.1: https://datatracker.ietf.org/doc/html/rfc5545#section-3.1
"""

import uuid

import pytest

from icalendar import (
    Alarm,
    Calendar,
    Event,
    FreeBusy,
    Journal,
    Todo,
)
from icalendar.attr import validate_uid
from icalendar.prop import vUid

COMPONENTS = [Calendar, Event, Todo, Journal, FreeBusy, Alarm]


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_valid_string_uid(component_cls):
    """UID setter accepts valid iana-token strings (alphanumeric and hyphens)."""
    comp = component_cls()
    comp.uid = "valid-uid-123"
    assert comp.uid == "valid-uid-123"


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_valid_uuid_object(component_cls):
    """UID setter accepts uuid.UUID instances."""
    comp = component_cls()
    u = uuid.uuid4()
    comp.uid = u
    assert str(comp.uid) == str(u)


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_letter_casing_preserved(component_cls):
    """UID setter preserves original letter casing without modification."""
    comp = component_cls()
    comp.uid = "MiXeD-CaSe-UiD-123"
    assert comp.uid == "MiXeD-CaSe-UiD-123"

    comp.uid = "UPPERCASE-123"
    assert comp.uid == "UPPERCASE-123"

    comp.uid = "lowercase-123"
    assert comp.uid == "lowercase-123"


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_uid_none_deletes_property(component_cls):
    """Setting UID to None deletes the UID property."""
    comp = component_cls()
    comp.uid = "valid-uid"
    assert comp.uid == "valid-uid"

    comp.uid = None
    assert comp.uid == ""
    assert "UID" not in comp


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_del_uid_deletes_property(component_cls):
    """Deleting UID removes the property."""
    comp = component_cls()
    comp.uid = "valid-uid"
    assert comp.uid == "valid-uid"

    del comp.uid
    assert comp.uid == ""
    assert "UID" not in comp


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_empty_uid_raises_value_error(component_cls):
    """Empty string raises ValueError."""
    comp = component_cls()
    with pytest.raises(ValueError, match="UID must not be empty"):
        comp.uid = ""


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_uid_octet_length_limit(component_cls):
    """UID must have a length strictly less than 255 octets per RFC 7986."""
    comp = component_cls()

    # 254 ASCII octets is valid
    valid_254 = "a" * 254
    comp.uid = valid_254
    assert comp.uid == valid_254

    # 255 octets is rejected
    too_long = "a" * 255
    with pytest.raises(ValueError, match="less than 255 octets"):
        comp.uid = too_long


@pytest.mark.parametrize("component_cls", COMPONENTS)
@pytest.mark.parametrize(
    "invalid_uid",
    [
        "has space",
        "email@example.com",
        "has_underscore",
        "domain.name",
        "slash/in/uid",
        "colon:123",
        "semicolon;123",
        "hash#tag",
        "unicode-ä-test",
    ],
)
def test_invalid_characters_raise_value_error(component_cls, invalid_uid):
    """Characters outside 1*(ALPHA / DIGIT / "-") raise ValueError."""
    comp = component_cls()
    with pytest.raises(ValueError, match="must conform to the iana-token syntax"):
        comp.uid = invalid_uid


@pytest.mark.parametrize("component_cls", COMPONENTS)
@pytest.mark.parametrize("invalid_type", [123, 45.6, ["a"], {"uid": "1"}])
def test_invalid_type_raises_type_error(component_cls, invalid_type):
    """Non-string and non-UUID types raise TypeError."""
    comp = component_cls()
    with pytest.raises(TypeError, match=r"UID must be a string or uuid\.UUID"):
        comp.uid = invalid_type


@pytest.mark.parametrize("component_cls", COMPONENTS)
def test_failed_assignment_does_not_mutate_existing_uid(component_cls):
    """An invalid assignment leaves existing UID intact."""
    comp = component_cls()
    comp.uid = "initial-uid-123"

    with pytest.raises(ValueError):
        comp.uid = "invalid@value"

    assert comp.uid == "initial-uid-123"


def test_validate_uid_function_and_class_method():
    """validate_uid and vUid.validate work directly."""
    validate_uid("good-uid")
    validate_uid(uuid.uuid4())
    vUid.validate("another-good-uid")

    with pytest.raises(ValueError):
        validate_uid("bad@uid")

    with pytest.raises(ValueError):
        vUid.validate("bad_uid")

    with pytest.raises(TypeError):
        validate_uid(999)
