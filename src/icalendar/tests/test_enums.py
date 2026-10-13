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


def test_get_returns_member_for_known_value():
    """get() with a valid value returns that member, like a dict."""
    assert enums.PARTSTAT.get("ACCEPTED") is enums.PARTSTAT.ACCEPTED
    assert enums.STATUS.get("TENTATIVE") is enums.STATUS.TENTATIVE


def test_get_returns_none_for_unknown_value():
    """get() with an unknown value returns None instead of raising."""
    assert enums.PARTSTAT.get("no-value") is None
    assert enums.STATUS.get("X-UNKNOWN") is None


def test_get_returns_default_for_unknown_value():
    """get() with a default returns that default for an unknown value."""
    assert enums.PARTSTAT.get("no-value", "other-value") == "other-value"
    assert enums.PARTSTAT.get("no-value", enums.PARTSTAT.ACCEPTED) is (
        enums.PARTSTAT.ACCEPTED
    )
    assert enums.STATUS.get("no-value", None) is None


def test_get_ignores_default_for_known_value():
    """A known value wins over the default, like dict.get()."""
    assert enums.PARTSTAT.get("DECLINED", "other-value") is enums.PARTSTAT.DECLINED


@pytest.mark.parametrize("enum_name", ENUMS)
def test_get_is_available_on_every_enum(enum_name):
    """get() must exist on all of the enums, not just PARTSTAT."""
    assert hasattr(getattr(enums, enum_name), "get")


def test_constructor_still_rejects_unknown_value():
    """get() must not change the strict behaviour of calling the enum itself.

    PARTSTAT("no-value") keeps raising ValueError: get() is the opt-in
    lenient path, not a global relaxation.
    """
    with pytest.raises(ValueError):
        enums.PARTSTAT("no-value")
