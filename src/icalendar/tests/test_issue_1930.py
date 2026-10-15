from typing_extensions import assert_type

from icalendar.prop.recur.recur import RecurEntryValue, vRecur


def test_vrecur_value_type():
    rule = vRecur.from_ical("FREQ=DAILY;COUNT=10")

    assert_type(rule["COUNT"], RecurEntryValue)
    assert rule["COUNT"] == [10]


def test_vrecur_value_type_with_multiple_values():
    rule = vRecur.from_ical("FREQ=DAILY;BYDAY=MO,TU,WE")

    assert_type(rule["BYDAY"], RecurEntryValue)
    assert rule["BYDAY"] == ["MO", "TU", "WE"]
