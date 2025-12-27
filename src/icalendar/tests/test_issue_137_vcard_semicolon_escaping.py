"""Test vCard property semicolon handling (Issue #137).

vCard structured properties (ADR, N, ORG) use semicolons as field separators per RFC 6350.
These semicolons should NOT be escaped, unlike iCalendar TEXT values.
"""

import pytest

from icalendar import Component
from icalendar.parser import split_on_unescaped_semicolon
from icalendar.prop import vAdr, vN, vOrg


class TestSplitOnUnescapedSemicolon:
    """Test the split_on_unescaped_semicolon helper function."""

    def test_simple_split(self):
        """Split on unescaped semicolons."""
        result = split_on_unescaped_semicolon("a;b;c")
        assert result == ["a", "b", "c"]

    def test_escaped_semicolons_not_split(self):
        """Escaped semicolons are not split points."""
        result = split_on_unescaped_semicolon(r"a\;b\;c")
        assert result == ["a;b;c"]

    def test_mixed_escaped_and_unescaped(self):
        """Mix of escaped and unescaped semicolons."""
        result = split_on_unescaped_semicolon(r"field1\;with;field2")
        assert result == ["field1;with", "field2"]

    def test_vcard_adr_example(self):
        """Example from vCard ADR."""
        result = split_on_unescaped_semicolon(r"PO Box 123\;Suite 200;City")
        assert result == ["PO Box 123;Suite 200", "City"]

    def test_empty_string(self):
        """Empty string returns single empty field."""
        result = split_on_unescaped_semicolon("")
        assert result == [""]

    def test_empty_fields(self):
        """Empty fields are preserved."""
        result = split_on_unescaped_semicolon(";;a;b;;c;")
        assert result == ["", "", "a", "b", "", "c", ""]


class TestVAdr:
    """Test vCard ADR (Address) property."""

    def test_adr_creation_with_tuple(self):
        """Create ADR from tuple of 7 fields."""
        adr = vAdr(("", "", "123 Main St", "Springfield", "IL", "62701", "USA"))
        assert adr.fields == (
            "",
            "",
            "123 Main St",
            "Springfield",
            "IL",
            "62701",
            "USA",
        )

    def test_adr_to_ical(self):
        """ADR to_ical generates semicolon-separated format."""
        adr = vAdr(("", "", "123 Main St", "Springfield", "IL", "62701", "USA"))
        result = adr.to_ical()
        assert result == b";;123 Main St;Springfield;IL;62701;USA"

    def test_adr_from_ical(self):
        """Parse ADR from vCard format."""
        result = vAdr.from_ical(";;123 Main St;Springfield;IL;62701;USA")
        assert result == ("", "", "123 Main St", "Springfield", "IL", "62701", "USA")

    def test_adr_round_trip(self):
        """ADR survives round-trip through to_ical and from_ical."""
        original = ("", "", "123 Main St", "Springfield", "IL", "62701", "USA")
        adr = vAdr(original)
        ical = adr.to_ical()
        parsed = vAdr.from_ical(ical)
        assert parsed == original

    def test_adr_semicolons_not_escaped(self):
        """Semicolons in ADR are field separators, not escaped."""
        adr = vAdr(
            ("PO Box 1", "Suite 200", "123 Main St", "City", "State", "12345", "USA")
        )
        ical = adr.to_ical()
        # Semicolons between fields should NOT be escaped
        assert b"\\;" not in ical  # No escaped semicolons
        assert ical.count(b";") == 6  # 6 semicolons for 7 fields

    def test_adr_commas_in_field(self):
        """Commas within ADR fields ARE escaped."""
        adr = vAdr(("", "", "123 Main St, Apt 4", "Springfield", "IL", "62701", "USA"))
        ical = adr.to_ical()
        # Comma within street field should be escaped
        assert b"\\," in ical

    def test_adr_semicolons_in_field_are_escaped(self):
        """Semicolons within ADR field values ARE escaped (different from field separators)."""
        adr = vAdr(("", "", "123 Main St; Apt 4", "Springfield", "IL", "62701", "USA"))
        ical = adr.to_ical()
        # Semicolon within street field value should be escaped
        assert b"\\;" in ical
        # Should have 6 unescaped semicolons (field separators) + 1 escaped (within field)
        # Total semicolons in bytes: 7, but 1 is preceded by backslash
        assert ical.count(b";") == 7  # 6 separators + 1 escaped

        # Round-trip: should preserve the semicolon in the field value
        parsed = vAdr.from_ical(ical)
        assert parsed[2] == "123 Main St; Apt 4"  # Street field with semicolon

    def test_adr_empty_fields(self):
        """Empty fields are preserved in ADR."""
        adr = vAdr(("", "", "123 Main St", "City", "", "12345", "USA"))
        ical = adr.to_ical()
        parsed = vAdr.from_ical(ical)
        assert parsed[0] == ""  # PO box empty
        assert parsed[1] == ""  # Extended address empty
        assert parsed[4] == ""  # Region empty

    def test_adr_requires_7_fields(self):
        """ADR must have exactly 7 fields."""
        with pytest.raises(ValueError, match="exactly 7 fields"):
            vAdr(("too", "few"))

    def test_issue_137_example(self):
        """Test the exact example from Issue #137."""
        # The issue shows ADR with this value part:
        # ;2822 Email HQ;Suite 2821;RFCVille;PA;1521$;USA
        adr_value = ";2822 Email HQ;Suite 2821;RFCVille;PA;1521$;USA"
        parsed = vAdr.from_ical(adr_value)
        assert len(parsed) == 7
        assert parsed[0] == ""  # PO box empty
        assert parsed[1] == "2822 Email HQ"  # Extended address
        assert parsed[2] == "Suite 2821"  # Street
        assert parsed[3] == "RFCVille"  # Locality
        assert parsed[4] == "PA"  # Region
        assert parsed[5] == "1521$"  # Postal code
        assert parsed[6] == "USA"  # Country

        # Round-trip should preserve structure
        adr = vAdr(parsed)
        regenerated = adr.to_ical().decode("utf-8")
        assert regenerated == adr_value


class TestVN:
    """Test vCard N (Name) property."""

    def test_n_creation_with_tuple(self):
        """Create N from tuple of 5 fields."""
        n = vN(("Doe", "John", "M.", "Dr.", "Jr."))
        assert n.fields == ("Doe", "John", "M.", "Dr.", "Jr.")

    def test_n_to_ical(self):
        """N to_ical generates semicolon-separated format."""
        n = vN(("Doe", "John", "M.", "Dr.", "Jr."))
        result = n.to_ical()
        assert result == b"Doe;John;M.;Dr.;Jr."

    def test_n_from_ical(self):
        """Parse N from vCard format."""
        result = vN.from_ical("Doe;John;M.;Dr.;Jr.")
        assert result == ("Doe", "John", "M.", "Dr.", "Jr.")

    def test_n_round_trip(self):
        """N survives round-trip through to_ical and from_ical."""
        original = ("Doe", "John", "Michael", "Dr.", "Jr.")
        n = vN(original)
        ical = n.to_ical()
        parsed = vN.from_ical(ical)
        assert parsed == original

    def test_n_semicolons_not_escaped(self):
        """Semicolons in N are field separators, not escaped."""
        n = vN(("Doe", "John", "M.", "Dr.", "Jr."))
        ical = n.to_ical()
        # Semicolons between fields should NOT be escaped
        assert b"\\;" not in ical
        assert ical.count(b";") == 4  # 4 semicolons for 5 fields

    def test_n_empty_fields(self):
        """Empty fields are preserved in N."""
        n = vN(("Doe", "John", "", "", ""))
        ical = n.to_ical()
        parsed = vN.from_ical(ical)
        assert parsed[2] == ""  # Additional names empty
        assert parsed[3] == ""  # Prefix empty
        assert parsed[4] == ""  # Suffix empty

    def test_n_requires_5_fields(self):
        """N must have exactly 5 fields."""
        with pytest.raises(ValueError, match="exactly 5 fields"):
            vN(("too", "few"))


class TestVOrg:
    """Test vCard ORG (Organization) property."""

    def test_org_creation_with_tuple(self):
        """Create ORG from tuple of fields."""
        org = vOrg(("ABC Inc.", "Marketing", "Sales"))
        assert org.fields == ("ABC Inc.", "Marketing", "Sales")

    def test_org_to_ical(self):
        """ORG to_ical generates semicolon-separated format."""
        org = vOrg(("ABC Inc.", "Marketing", "Sales"))
        result = org.to_ical()
        assert result == b"ABC Inc.;Marketing;Sales"

    def test_org_from_ical(self):
        """Parse ORG from vCard format."""
        result = vOrg.from_ical("ABC Inc.;Marketing;Sales")
        assert result == ("ABC Inc.", "Marketing", "Sales")

    def test_org_round_trip(self):
        """ORG survives round-trip through to_ical and from_ical."""
        original = ("ABC Inc.", "North American Division", "Marketing")
        org = vOrg(original)
        ical = org.to_ical()
        parsed = vOrg.from_ical(ical)
        assert parsed == original

    def test_org_variable_length(self):
        """ORG supports variable number of organizational units."""
        # Just organization name
        org1 = vOrg(("ABC Inc.",))
        assert len(org1.fields) == 1

        # Organization with 2 units
        org2 = vOrg(("ABC Inc.", "Marketing"))
        assert len(org2.fields) == 2

        # Organization with many units
        org3 = vOrg(("ABC Inc.", "North America", "USA", "California", "Marketing"))
        assert len(org3.fields) == 5

    def test_org_semicolons_not_escaped(self):
        """Semicolons in ORG are field separators, not escaped."""
        org = vOrg(("ABC Inc.", "Marketing", "Sales"))
        ical = org.to_ical()
        # Semicolons between fields should NOT be escaped
        assert b"\\;" not in ical
        assert ical.count(b";") == 2  # 2 semicolons for 3 fields

    def test_org_requires_at_least_one_field(self):
        """ORG must have at least 1 field (organization name)."""
        with pytest.raises(ValueError, match="at least 1 field"):
            vOrg(())


class TestComponentIntegration:
    """Test vCard properties work within Component parsing."""

    def test_adr_in_component(self):
        """ADR property works in a Component."""
        comp = Component()
        comp.add("ADR", ("", "", "123 Main St", "City", "State", "12345", "USA"))
        ical = comp.to_ical()
        assert b"ADR:;;123 Main St;City;State;12345;USA" in ical

    def test_n_in_component(self):
        """N property works in a Component."""
        comp = Component()
        comp.add("N", ("Doe", "John", "M.", "Dr.", "Jr."))
        ical = comp.to_ical()
        assert b"N:Doe;John;M.;Dr.;Jr." in ical

    def test_org_in_component(self):
        """ORG property works in a Component."""
        comp = Component()
        comp.add("ORG", ("ABC Inc.", "Marketing"))
        ical = comp.to_ical()
        assert b"ORG:ABC Inc.;Marketing" in ical

    def test_vcard_in_vcalendar(self):
        """vCard properties can appear in VCALENDAR (non-standard but possible)."""
        ical_data = b"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//EN
ADR:;;123 Main St;Springfield;IL;62701;USA
END:VCALENDAR
"""
        cal = Component.from_ical(ical_data)
        assert "ADR" in cal
        adr_value = cal["ADR"]
        # Should be parsed as vAdr
        assert isinstance(adr_value, vAdr)
        assert adr_value.fields[2] == "123 Main St"  # Street field
