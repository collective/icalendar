"""Coverage tests for uncovered branches in :mod:`icalendar.prop.org`.

These tests target the branches identified in the coverage survey:

- ``vOrg.__eq__`` — the ``isinstance`` False branch (comparing with non-vOrg).
- ``vOrg.__repr__`` — string representation.
- ``vOrg.from_jcal`` — the happy path (valid jCal with string fields) and
  the ``validate_value_type`` loop (non-string field value).
"""

from __future__ import annotations

import pytest

from icalendar.error import JCalParsingError
from icalendar.prop import vOrg


class TestVOrgEquality:
    """Test ``vOrg.__eq__``."""

    def test_eq_same_fields(self):
        """Two vOrg instances with the same fields are equal."""
        org1 = vOrg(("ABC Inc.", "Marketing", "Sales"))
        org2 = vOrg(("ABC Inc.", "Marketing", "Sales"))
        assert org1 == org2

    def test_eq_different_fields(self):
        """Two vOrg instances with different fields are not equal."""
        org1 = vOrg(("ABC Inc.", "Marketing"))
        org2 = vOrg(("ABC Inc.", "Sales"))
        assert org1 != org2

    def test_eq_different_number_of_fields(self):
        """Two vOrg instances with a different number of fields are not equal."""
        org1 = vOrg(("ABC Inc.", "Marketing"))
        org2 = vOrg(("ABC Inc.", "Marketing", "Sales"))
        assert org1 != org2

    def test_eq_non_vorg_object(self):
        """A vOrg is not equal to a non-vOrg object (isinstance False branch)."""
        org = vOrg(("ABC Inc.", "Marketing"))
        assert org != "ABC Inc.;Marketing"
        assert org != ("ABC Inc.", "Marketing")
        assert org != 42
        assert org != None  # noqa: E711


class TestVOrgRepr:
    """Test ``vOrg.__repr__``."""

    def test_repr_contains_class_name_and_fields(self):
        """repr includes the class name and the fields tuple."""
        org = vOrg(("ABC Inc.", "Marketing", "Sales"))
        result = repr(org)
        assert result.startswith("vOrg(")
        assert "('ABC Inc.', 'Marketing', 'Sales')" in result

    def test_repr_contains_params(self):
        """repr includes the params."""
        org = vOrg(("ABC Inc.", "Marketing"), params={"LANGUAGE": "en"})
        result = repr(org)
        assert "params=" in result
        assert "LANGUAGE" in result

    def test_repr_round_trip_not_equal_to_string(self):
        """repr is a string, not the same as to_ical."""
        org = vOrg(("ABC Inc.", "Marketing"))
        result = repr(org)
        assert isinstance(result, str)
        assert "ABC Inc." in result


class TestVOrgFromJcal:
    """Test ``vOrg.from_jcal``."""

    def test_from_jcal_valid(self):
        """Parse a valid jCal ORG property into a vOrg."""
        jcal = ["org", {}, "text", "ABC Inc.", "Marketing", "Sales"]
        org = vOrg.from_jcal(jcal)
        assert org.fields == ("ABC Inc.", "Marketing", "Sales")
        assert org.params == {}

    def test_from_jcal_single_field(self):
        """Parse a jCal ORG property with only the organization name."""
        jcal = ["org", {}, "text", "ABC Inc."]
        org = vOrg.from_jcal(jcal)
        assert org.fields == ("ABC Inc.",)
        assert org.name == "ABC Inc."
        assert org.units == ()

    def test_from_jcal_with_params(self):
        """Parse a jCal ORG property that has parameters."""
        jcal = ["org", {"language": "en"}, "text", "ABC Inc.", "Marketing"]
        org = vOrg.from_jcal(jcal)
        assert org.fields == ("ABC Inc.", "Marketing")
        assert org.params["language"] == "en"

    def test_from_jcal_round_trip(self):
        """to_jcal and from_jcal round-trip preserves the vOrg."""
        original = vOrg(("ABC Inc.", "North American Division", "Marketing"))
        jcal = original.to_jcal("org")
        parsed = vOrg.from_jcal(jcal)
        assert parsed == original
        assert parsed.fields == original.fields

    def test_from_jcal_non_string_field(self):
        """A non-string field value raises JCalParsingError."""
        jcal = ["org", {}, "text", 123, "Marketing"]
        with pytest.raises(
            JCalParsingError,
            match=r"\[3\] in vOrg: The value must be a string\.",
        ):
            vOrg.from_jcal(jcal)

    def test_from_jcal_non_string_field_at_index_4(self):
        """A non-string field value at a later index also raises."""
        jcal = ["org", {}, "text", "ABC Inc.", 456]
        with pytest.raises(
            JCalParsingError,
            match=r"\[4\] in vOrg: The value must be a string\.",
        ):
            vOrg.from_jcal(jcal)

    def test_from_jcal_too_short_raises(self):
        """A jCal property with fewer than 4 elements raises JCalParsingError.

        This is caught by ``JCalParsingError.validate_property``.
        """
        jcal = ["org", {}, "text"]
        with pytest.raises(
            JCalParsingError,
            match=r"in vOrg: The property must be a list with at least 4 items\.",
        ):
            vOrg.from_jcal(jcal)
