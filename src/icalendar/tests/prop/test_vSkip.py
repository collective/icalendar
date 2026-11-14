"""Tests for vSkip.ical_value (issue #876)."""

import pytest

from icalendar.prop import vSkip


@pytest.mark.parametrize(
    ("skip", "expected"),
    [
        (vSkip.OMIT, "OMIT"),
        (vSkip.FORWARD, "FORWARD"),
        (vSkip.BACKWARD, "BACKWARD"),
    ],
)
def test_ical_value_is_the_rfc_7529_token(skip, expected):
    """ical_value returns the RFC 7529 SKIP token, not the enum name."""
    assert skip.ical_value == expected


@pytest.mark.parametrize("skip", list(vSkip))
def test_ical_value_is_a_plain_str(skip):
    """ical_value is a plain str, not a vText (isinstance would accept both)."""
    assert type(skip.ical_value) is str
