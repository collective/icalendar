"""Test vMonth ical_value property."""

from icalendar.prop import vMonth


def test_ical_value_basic():
    """ical_value property returns int for month number."""
    m = vMonth(5)
    assert m.ical_value == 5
    assert isinstance(m.ical_value, int)


def test_ical_value_all_months():
    """ical_value property works for all month numbers."""
    for month_num in range(1, 13):
        m = vMonth(month_num)
        assert m.ical_value == month_num


def test_ical_value_leap_month():
    """ical_value property returns int for leap month (without L)."""
    m = vMonth("5L")
    assert m.ical_value == 5
    assert m.leap is True
    # ical_value returns just the number, not the L suffix


def test_ical_value_from_string():
    """ical_value property works with month created from string."""
    m = vMonth("3")
    assert m.ical_value == 3
    assert m.leap is False


def test_ical_value_from_ical():
    """ical_value property works with month parsed from ical string."""
    m = vMonth.from_ical("7")
    assert m.ical_value == 7

    m_leap = vMonth.from_ical("2L")
    assert m_leap.ical_value == 2
    assert m_leap.leap is True


def test_ical_value_january():
    """ical_value property returns 1 for January."""
    m = vMonth(1)
    assert m.ical_value == 1


def test_ical_value_december():
    """ical_value property returns 12 for December."""
    m = vMonth(12)
    assert m.ical_value == 12


def test_ical_value_arithmetic():
    """ical_value can be used in arithmetic operations."""
    m = vMonth(6)
    assert m.ical_value + 1 == 7
    assert m.ical_value * 2 == 12
