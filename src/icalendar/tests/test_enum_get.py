"""Tests for StrEnum.get classmethod (#1921)."""
import pytest
from icalendar import PARTSTAT


class TestStrEnumGet:
    def test_get_valid_value_returns_member(self):
        assert PARTSTAT.get("ACCEPTED") is PARTSTAT.ACCEPTED

    def test_get_invalid_value_returns_none_by_default(self):
        assert PARTSTAT.get("no-value") is None

    def test_get_invalid_value_returns_default(self):
        assert PARTSTAT.get("no-value", "fallback") == "fallback"

    def test_get_does_not_raise(self):
        try:
            PARTSTAT.get("anything-weird-!@#")
        except ValueError:
            pytest.fail("StrEnum.get() should not raise ValueError")

    def test_documentation_example(self):
        assert PARTSTAT.get("no-value") is None
        assert PARTSTAT.get("no-value", "other-value") == "other-value"
