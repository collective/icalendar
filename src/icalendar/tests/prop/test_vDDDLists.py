"""Test vDDDLists ical_value property."""

from datetime import date, datetime, timedelta

from icalendar.prop import vDDDLists


def test_ical_value_single():
    """ical_value property returns the list of vDDDTypes."""
    dt = datetime(2021, 3, 2, 10, 15, 0)
    vddd_list = vDDDLists([dt])
    
    assert isinstance(vddd_list.ical_value, list)
    assert len(vddd_list.ical_value) == 1
    assert vddd_list.ical_value[0].dt == dt


def test_ical_value_multiple():
    """ical_value property returns list with multiple values."""
    dt1 = datetime(2021, 3, 2, 10, 0, 0)
    dt2 = datetime(2021, 3, 3, 14, 30, 0)
    dt3 = date(2021, 3, 4)
    
    vddd_list = vDDDLists([dt1, dt2, dt3])
    
    assert isinstance(vddd_list.ical_value, list)
    assert len(vddd_list.ical_value) == 3
    assert vddd_list.ical_value[0].dt == dt1
    assert vddd_list.ical_value[1].dt == dt2
    assert vddd_list.ical_value[2].dt == dt3


def test_ical_value_mixed_types():
    """ical_value property handles mixed date/time types."""
    dt = datetime(2021, 3, 2, 10, 0, 0)
    d = date(2021, 3, 3)
    td = timedelta(hours=2)
    
    vddd_list = vDDDLists([dt, d, td])
    
    assert isinstance(vddd_list.ical_value, list)
    assert len(vddd_list.ical_value) == 3
