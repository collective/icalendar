"""Test vRecur ical_value property."""

from icalendar.prop import vRecur


def test_ical_value_basic():
    """ical_value property returns dict for recurrence rule."""
    rrule = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    value = rrule.ical_value
    assert isinstance(value, dict)
    assert "FREQ" in value
    assert "COUNT" in value


def test_ical_value_daily_count():
    """ical_value property returns correct dict for DAILY with COUNT."""
    rrule = vRecur.from_ical("FREQ=DAILY;COUNT=10")
    value = rrule.ical_value
    assert value["FREQ"] == ["DAILY"]
    assert value["COUNT"] == [10]


def test_ical_value_weekly_byday():
    """ical_value property returns correct dict for WEEKLY with BYDAY."""
    rrule = vRecur.from_ical("FREQ=WEEKLY;BYDAY=MO,WE,FR")
    value = rrule.ical_value
    assert value["FREQ"] == ["WEEKLY"]
    assert "BYDAY" in value
    assert len(value["BYDAY"]) == 3


def test_ical_value_monthly_interval():
    """ical_value property returns correct dict for MONTHLY with INTERVAL."""
    rrule = vRecur.from_ical("FREQ=MONTHLY;INTERVAL=2")
    value = rrule.ical_value
    assert value["FREQ"] == ["MONTHLY"]
    assert value["INTERVAL"] == [2]


def test_ical_value_yearly_bymonth():
    """ical_value property returns correct dict for YEARLY with BYMONTH."""
    rrule = vRecur.from_ical("FREQ=YEARLY;BYMONTH=1,7")
    value = rrule.ical_value
    assert value["FREQ"] == ["YEARLY"]
    assert "BYMONTH" in value
    assert len(value["BYMONTH"]) == 2


def test_ical_value_complex_rule():
    """ical_value property returns correct dict for complex rule."""
    rrule = vRecur.from_ical("FREQ=MONTHLY;BYDAY=MO;BYSETPOS=-1;COUNT=12")
    value = rrule.ical_value
    assert value["FREQ"] == ["MONTHLY"]
    assert "BYDAY" in value
    assert "BYSETPOS" in value
    assert value["COUNT"] == [12]


def test_ical_value_from_constructor():
    """ical_value property works with vRecur created from constructor."""
    rrule = vRecur(FREQ="DAILY", COUNT=5)
    value = rrule.ical_value
    assert value["FREQ"] == ["DAILY"]
    assert value["COUNT"] == [5]


def test_ical_value_wkst():
    """ical_value property returns correct dict with WKST."""
    rrule = vRecur.from_ical("FREQ=WEEKLY;WKST=MO")
    value = rrule.ical_value
    assert value["FREQ"] == ["WEEKLY"]
    assert "WKST" in value
