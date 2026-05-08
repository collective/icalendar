"""Test vDuration ical_value property."""

from datetime import timedelta

from icalendar.prop import vDuration


def test_ical_value_basic():
    """ical_value property returns timedelta object."""
    td = timedelta(days=15, hours=5, seconds=20)
    dur = vDuration(td)
    assert dur.ical_value == td
    assert isinstance(dur.ical_value, timedelta)


def test_ical_value_components():
    """ical_value property components match days and seconds."""
    td = timedelta(days=7, hours=3, minutes=30, seconds=45)
    dur = vDuration(td)
    assert dur.ical_value.days == 7
    assert dur.ical_value.seconds == 12645  # 3*3600 + 30*60 + 45
    assert dur.ical_value.total_seconds() == 617445.0


def test_ical_value_from_ical():
    """ical_value property works with duration parsed from ical string."""
    td = vDuration.from_ical("P15DT5H0M20S")
    dur = vDuration(td)
    assert dur.ical_value == timedelta(days=15, hours=5, seconds=20)

    # Weeks
    td_weeks = vDuration.from_ical("P7W")
    dur_weeks = vDuration(td_weeks)
    assert dur_weeks.ical_value == timedelta(weeks=7)


def test_ical_value_negative():
    """ical_value property handles negative durations."""
    td = timedelta(days=-5, hours=-2)
    dur = vDuration(td)
    assert dur.ical_value == td
    assert dur.ical_value.days == -6  # timedelta normalizes to -6 days + 79200 seconds
    assert dur.ical_value.total_seconds() == -439200.0  # -5*86400 - 2*3600 = -439200


def test_ical_value_zero():
    """ical_value property handles zero duration."""
    td = timedelta(0)
    dur = vDuration(td)
    assert dur.ical_value == td
    assert dur.ical_value.total_seconds() == 0.0


def test_ical_value_from_string():
    """ical_value property works when vDuration is created from string."""
    dur = vDuration("P1DT12H")
    assert dur.ical_value == timedelta(days=1, hours=12)
    assert dur.ical_value.total_seconds() == 129600.0
