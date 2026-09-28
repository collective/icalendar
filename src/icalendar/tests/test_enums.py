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


def test_enum_values_are_case_insensitive(enum):
    """Enumerated property values are case-insensitive per RFC 5545 section 3.1."""
    for member in enum:
        assert enum(member.value.lower()) is member
        assert enum(member.value.upper()) is member
        assert enum(member.value.swapcase()) is member


def test_partstat_accepts_case_insensitive_values():
    """PARTSTAT resolves differently-cased values to the same member (issue #1840)."""
    assert enums.PARTSTAT("needs-action") == enums.PARTSTAT.NEEDS_ACTION
    assert enums.PARTSTAT("needs-action") is enums.PARTSTAT.NEEDS_ACTION


def test_enum_raises_for_unknown_values(enum):
    """Unknown values still raise a ValueError."""
    for value in ("NOT-A-VALUE", ""):
        with pytest.raises(ValueError):
            enum(value)


def test_enum_raises_for_non_string_values(enum):
    """Non-string values are not matched case-insensitively."""
    for value in (None, 123, b"NEEDS-ACTION"):
        with pytest.raises(ValueError):
            enum(value)
