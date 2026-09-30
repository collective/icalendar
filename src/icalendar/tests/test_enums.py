"""Test the enums for values."""

import pickle

import pytest

import icalendar
from icalendar import enums

ENUMS = [
    name
    for name in enums.__all__
    if isinstance(getattr(enums, name), type)
    and issubclass(getattr(enums, name), enums.Enum)
]


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


def test_partstat_accepts_lowercase_value():
    """PARTSTAT accepts case-insensitive values, as in issue #1840."""
    assert (
        enums.PARTSTAT("needs-action")
        == enums.PARTSTAT("NEEDS-ACTION")
        == enums.PARTSTAT.NEEDS_ACTION
    )


def test_enum_lookup_is_case_insensitive(enum_name):
    """Every enum resolves each of its values regardless of case."""
    enum = getattr(enums, enum_name)
    for member in enum:
        assert enum(member.value.lower()) is member
        assert enum(member.value.upper()) is member
        assert enum(member.value.swapcase()) is member


def test_enum_lookup_is_case_insensitive_for_members_that_differ_by_more_than_case():
    """Members of the same enum that differ by more than case stay distinct."""
    assert enums.RELATED("start") is enums.RELATED.START
    assert enums.RELATED("end") is enums.RELATED.END
    assert enums.RELATED.START is not enums.RELATED.END


@pytest.mark.parametrize(
    "value",
    [
        "nonsense",
        "",
        "needs action",
        "NEEDS_ACTION",
        None,
        1,
    ],
)
def test_enum_lookup_rejects_invalid_values(value):
    """A value that is not a member still raises ValueError."""
    with pytest.raises(ValueError, match="is not a valid PARTSTAT"):
        enums.PARTSTAT(value)


def test_enum_values_serialize_unchanged():
    """Case-insensitive lookup does not change what is serialized."""
    assert str(enums.PARTSTAT.NEEDS_ACTION) == "NEEDS-ACTION"
    assert enums.PARTSTAT("needs-action").value == "NEEDS-ACTION"
    assert enums.PARTSTAT("needs-action") == "NEEDS-ACTION"


@pytest.mark.parametrize(
    ("enum_name", "value"),
    [
        ("STATUS", "start"),
        ("RELATED", "accepted"),
        ("PARTSTAT", "public"),
        ("CUTYPE", "needs-action"),
    ],
)
def test_enum_lookup_does_not_leak_members_from_another_enum(enum_name, value):
    """A value belonging to a different enum is not resolved."""
    enum = getattr(enums, enum_name)
    with pytest.raises(ValueError, match=f"is not a valid {enum_name}"):
        enum(value)
