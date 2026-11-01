import pytest

from icalendar.prop import vFrequency


def test_valid_frequencies():
    """vFrequency accepts every RFC 5545 frequency value."""
    for freq in (
        "SECONDLY",
        "MINUTELY",
        "HOURLY",
        "DAILY",
        "WEEKLY",
        "MONTHLY",
        "YEARLY",
    ):
        assert vFrequency(freq).to_ical() == freq.encode("utf-8")


def test_case_insensitive():
    """vFrequency accepts lowercase input and uppercases it on serialization."""
    assert vFrequency.from_ical("weekly").to_ical() == b"WEEKLY"


def test_roundtrip():
    assert vFrequency.from_ical(vFrequency("DAILY").to_ical()) == "DAILY"


def test_error():
    """Error: Expected frequency, got: BOGUS"""
    with pytest.raises(ValueError):
        vFrequency.from_ical("BOGUS")


def test_ical_value():
    """ical_value property returns the frequency string value."""
    assert vFrequency("WEEKLY").ical_value == "WEEKLY"
    assert vFrequency("DAILY").ical_value == "DAILY"
    assert vFrequency("YEARLY").ical_value == "YEARLY"
    assert isinstance(vFrequency("WEEKLY").ical_value, str)
