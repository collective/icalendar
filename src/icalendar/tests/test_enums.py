"""Test the enums for values."""

import pickle

import pytest

import icalendar
from icalendar import enums

ENUMS = [name for name in dir(enums) if name.isupper()]


@pytest.fixture(params=ENUMS)
def enum_name(request):
    """The name of an enum"""
    return request.param


@pytest.fixture
def enum(enum_name):
    """An enum."""
    return getattr(enums, enum_name)


def test_all_enums_are_exported(enum_name):
    """All enums should be exported."""
    assert enum_name in enums.__all__


def test_all_enums_are_public(enum_name):
    """All enums should be exported."""
    assert enum_name in icalendar.__all__, f"icalendar.__all__ is missing {enum_name}"


def test_enum_has_description(enum):
    """We should have a docstring."""
    assert "Description:" in enum.__doc__


def test_enum_can_be_pickled():
    """Enum members retain their identity after a pickle round trip."""
    related = enums.RELATED.START

    assert pickle.loads(pickle.dumps(related)) is related  # noqa: S301


def test_value_enum_includes_binary():
    """BINARY is an RFC 5545 (section 3.2.20) value type and must be present."""
    assert enums.VALUE.BINARY == "BINARY"


def test_value_enum_matches_rfc_5545_value_types():
    """VALUE lists every value type defined in RFC 5545, section 3.2.20."""
    rfc_5545_value_types = {
        "BINARY",
        "BOOLEAN",
        "CAL-ADDRESS",
        "DATE",
        "DATE-TIME",
        "DURATION",
        "FLOAT",
        "INTEGER",
        "PERIOD",
        "RECUR",
        "TEXT",
        "TIME",
        "URI",
        "UTC-OFFSET",
    }
    assert {member.value for member in enums.VALUE} == rfc_5545_value_types


def test_vbinary_default_value_is_a_value_enum_member():
    """vBinary serializes as VALUE=BINARY, so BINARY must exist in VALUE."""
    from icalendar.prop import vBinary

    assert vBinary.default_value in {member.value for member in enums.VALUE}


def test_enums_accept_case_insensitive_values(enum):
    """Values that are not enclosed in double quotes are case-insensitive.

    See :rfc:`5545`, Section 3.1.
    """
    for member in enum:
        assert enum(member.value.lower()) is member
        assert enum(member.value.title()) is member


def test_partstat_example_is_case_insensitive():
    """The example from the report: PARTSTAT accepts any casing."""
    needs_action = enums.PARTSTAT.NEEDS_ACTION

    assert enums.PARTSTAT("needs-action") == needs_action
    assert enums.PARTSTAT("NEEDS-ACTION") == needs_action
    assert enums.PARTSTAT("nEeDs-AcTiOn") is needs_action


def test_unknown_enum_values_raise_value_error(enum):
    """An unknown value is still rejected instead of becoming a member."""
    with pytest.raises(ValueError, match="is not a valid"):
        enum("no-such-member")


def test_lowercase_property_values_are_read_from_calendars():
    """A value such as ``STATUS:confirmed`` maps to the enum member."""
    event = icalendar.Event.from_ical(
        "BEGIN:VEVENT\r\nUID:1\r\nDTSTAMP:20240101T000000Z\r\n"
        "DTSTART:20240101T000000Z\r\nSTATUS:confirmed\r\n"
        "TRANSP:transparent\r\nEND:VEVENT"
    )

    assert event.status is enums.STATUS.CONFIRMED
    assert event.transparency is enums.TRANSP.TRANSPARENT
