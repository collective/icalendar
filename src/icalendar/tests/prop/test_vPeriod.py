"""Test vPeriod ical_value property."""

from datetime import datetime, timedelta

from icalendar.prop import vPeriod


def test_ical_value_explicit_period():
    """ical_value property returns (start, end) for explicit period."""
    start = datetime(1997, 1, 1, 18, 0, 0)
    end = datetime(1997, 1, 2, 7, 0, 0)
    
    period = vPeriod((start, end))
    ical_val = period.ical_value
    
    assert isinstance(ical_val, tuple)
    assert len(ical_val) == 2
    assert ical_val[0] == start
    assert ical_val[1] == end
    assert isinstance(ical_val[1], datetime)


def test_ical_value_duration_period():
    """ical_value property returns (start, duration) for duration-based period."""
    start = datetime(1997, 1, 1, 18, 0, 0)
    duration = timedelta(hours=5, minutes=30)
    
    period = vPeriod((start, duration))
    ical_val = period.ical_value
    
    assert isinstance(ical_val, tuple)
    assert len(ical_val) == 2
    assert ical_val[0] == start
    assert ical_val[1] == duration
    assert isinstance(ical_val[1], timedelta)


def test_ical_value_preserves_original_form():
    """ical_value preserves the original form (explicit vs duration)."""
    start = datetime(2021, 3, 2, 10, 0, 0)
    
    # Explicit period
    end = datetime(2021, 3, 2, 12, 0, 0)
    period1 = vPeriod((start, end))
    assert period1.by_duration is False
    assert isinstance(period1.ical_value[1], datetime)
    
    # Duration period
    duration = timedelta(hours=2)
    period2 = vPeriod((start, duration))
    assert period2.by_duration is True
    assert isinstance(period2.ical_value[1], timedelta)
