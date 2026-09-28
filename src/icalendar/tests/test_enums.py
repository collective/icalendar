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


@pytest.mark.parametrize(
    ("enum_cls", "lower", "canonical"),
    [
        (enums.PARTSTAT, "needs-action", enums.PARTSTAT.NEEDS_ACTION),
        (enums.PARTSTAT, "NEEDS-ACTION", enums.PARTSTAT.NEEDS_ACTION),
        (enums.PARTSTAT, "Accepted", enums.PARTSTAT.ACCEPTED),
        (enums.STATUS, "tentative", enums.STATUS.TENTATIVE),
        (enums.FBTYPE, "busy-unavailable", enums.FBTYPE.BUSY_UNAVAILABLE),
        (enums.CUTYPE, "individual", enums.CUTYPE.INDIVIDUAL),
        (enums.ROLE, "req-participant", enums.ROLE.REQ_PARTICIPANT),
        (enums.TRANSP, "transparent", enums.TRANSP.TRANSPARENT),
        (enums.CLASS, "private", enums.CLASS.PRIVATE),
        (enums.VALUE, "date-time", enums.VALUE.DATE_TIME),
    ],
)
def test_str_enums_accept_case_insensitive_values(enum_cls, lower, canonical):
    """RFC 5545 enumerated values that are not quoted are case-insensitive."""
    assert enum_cls(lower) is canonical
    assert enum_cls(lower) == enum_cls(canonical.value) == canonical


def test_partstat_example_from_issue_1840():
    """The example requested in issue #1840 must hold."""
    assert (
        enums.PARTSTAT("needs-action")
        == enums.PARTSTAT("NEEDS-ACTION")
        == enums.PARTSTAT.NEEDS_ACTION
    )


def test_unknown_enum_value_still_raises():
    """Unrecognized values must still raise ValueError."""
    with pytest.raises(ValueError):
        enums.PARTSTAT("not-a-real-status")
