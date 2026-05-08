"""Test vFrequency ical_value property."""

import pytest

from icalendar.prop import vFrequency


def test_ical_value_daily():
    """ical_value property returns string for DAILY frequency."""
    freq = vFrequency("DAILY")
    assert freq.ical_value == "DAILY"
    assert isinstance(freq.ical_value, str)


def test_ical_value_all_frequencies():
    """ical_value property works for all valid frequencies."""
    frequencies = [
        "SECONDLY",
        "MINUTELY",
        "HOURLY",
        "DAILY",
        "WEEKLY",
        "MONTHLY",
        "YEARLY",
    ]
    for f in frequencies:
        freq = vFrequency(f)
        assert freq.ical_value == f


def test_ical_value_from_ical():
    """ical_value property works with frequency parsed from ical string."""
    freq = vFrequency.from_ical("WEEKLY")
    assert freq.ical_value == "WEEKLY"

    freq2 = vFrequency.from_ical("MONTHLY")
    assert freq2.ical_value == "MONTHLY"


def test_ical_value_case_insensitive():
    """ical_value property handles case-insensitive input."""
    freq_lower = vFrequency("daily")
    freq_upper = vFrequency("DAILY")
    # Both should normalize to uppercase
    assert freq_lower.ical_value.upper() == "DAILY"
    assert freq_upper.ical_value == "DAILY"


def test_ical_value_invalid_frequency():
    """vFrequency raises ValueError for invalid frequency."""
    with pytest.raises(ValueError, match="Expected frequency"):
        vFrequency("INVALID")


def test_ical_value_weekly():
    """ical_value property returns WEEKLY."""
    freq = vFrequency("WEEKLY")
    assert freq.ical_value == "WEEKLY"


def test_ical_value_yearly():
    """ical_value property returns YEARLY."""
    freq = vFrequency("YEARLY")
    assert freq.ical_value == "YEARLY"
