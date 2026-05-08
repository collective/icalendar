"""Test vUTCOffset ical_value property."""

from datetime import timedelta

from icalendar.prop import vUTCOffset


def test_ical_value_positive_offset():
    """ical_value property returns timedelta for positive UTC offset."""
    td = timedelta(hours=1)  # +01:00 (Geneva)
    offset = vUTCOffset(td)
    assert offset.ical_value == td
    assert offset.ical_value.total_seconds() == 3600


def test_ical_value_negative_offset():
    """ical_value property returns timedelta for negative UTC offset."""
    td = timedelta(hours=-5)  # -05:00 (New York)
    offset = vUTCOffset(td)
    assert offset.ical_value == td
    assert offset.ical_value.total_seconds() == -18000


def test_ical_value_from_ical():
    """ical_value property works with offset parsed from ical string."""
    td = vUTCOffset.from_ical("-0500")
    offset = vUTCOffset(td)
    assert offset.ical_value == timedelta(hours=-5)

    td_positive = vUTCOffset.from_ical("+0100")
    offset_positive = vUTCOffset(td_positive)
    assert offset_positive.ical_value == timedelta(hours=1)


def test_ical_value_with_minutes():
    """ical_value property handles offsets with minutes."""
    td = timedelta(hours=5, minutes=30)  # +05:30 (India)
    offset = vUTCOffset(td)
    assert offset.ical_value == td
    assert offset.ical_value.total_seconds() == 19800


def test_ical_value_zero_offset():
    """ical_value property handles zero offset (UTC)."""
    td = timedelta(0)
    offset = vUTCOffset(td)
    assert offset.ical_value == td
    assert offset.ical_value.total_seconds() == 0
