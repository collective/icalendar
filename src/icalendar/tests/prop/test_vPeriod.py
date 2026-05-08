"""Test vPeriod ical_value property."""

from datetime import datetime, timedelta

from icalendar.prop import vPeriod


def test_ical_value_explicit_period():
    """ical_value property returns (start, end) for explicit period."""
    start = datetime(1997, 1, 1, 18, 0, 0)
    end = datetime(1997, 1, 2, 7, 0, 0)
    period = vPeriod((start, end))

    assert period.ical_value == (start, end)
    assert isinstance(period.ical_value, tuple)
    assert len(period.ical_value) == 2
    assert isinstance(period.ical_value[0], datetime)
    assert isinstance(period.ical_value[1], datetime)


def test_ical_value_duration_period():
    """ical_value property returns (start, duration) for period by duration."""
    start = datetime(1997, 1, 1, 18, 0, 0)
    duration = timedelta(hours=5, minutes=30)
    period = vPeriod((start, duration))

    assert period.ical_value == (start, duration)
    assert isinstance(period.ical_value, tuple)
    assert len(period.ical_value) == 2
    assert isinstance(period.ical_value[0], datetime)
    assert isinstance(period.ical_value[1], timedelta)


def test_ical_value_components():
    """ical_value property components can be accessed individually."""
    start = datetime(2026, 5, 8, 10, 0, 0)
    end = datetime(2026, 5, 8, 12, 30, 0)
    period = vPeriod((start, end))

    period_start, period_end = period.ical_value
    assert period_start == start
    assert period_end == end


def test_ical_value_from_ical_explicit():
    """ical_value property works with explicit period parsed from ical string."""
    # Parse explicit period (start/end)
    per = vPeriod.from_ical("19970101T180000Z/19970102T070000Z")
    period = vPeriod(per)

    start, end = period.ical_value
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)
    assert start < end


def test_ical_value_from_ical_duration():
    """ical_value property works with duration period parsed from ical string."""
    # Parse period by duration
    per = vPeriod.from_ical("19970101T180000Z/PT5H30M")
    period = vPeriod(per)

    start, duration = period.ical_value
    assert isinstance(start, datetime)
    assert isinstance(duration, timedelta)
    assert duration == timedelta(hours=5, minutes=30)


def test_ical_value_preserves_original_form():
    """ical_value property preserves whether period was created with end or duration."""
    start = datetime(2026, 1, 1, 10, 0, 0)

    # Created with end datetime
    period_explicit = vPeriod((start, datetime(2026, 1, 1, 12, 0, 0)))
    _, second_explicit = period_explicit.ical_value
    assert isinstance(second_explicit, datetime)

    # Created with duration
    period_duration = vPeriod((start, timedelta(hours=2)))
    _, second_duration = period_duration.ical_value
    assert isinstance(second_duration, timedelta)
