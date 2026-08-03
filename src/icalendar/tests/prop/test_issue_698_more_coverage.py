import pytest

from icalendar.error import JCalParsingError
from icalendar.prop import vCategory, vDate, vUnknown, vWeekday


def test_vunknown_repr():
    repr_str = repr(vUnknown("a;b"))
    assert repr_str == "vUnknown(b'a;b')"


def test_vcategory_hash():
    category = vCategory(["WORK", "PERSONAL"])
    assert hash(category) == hash(tuple(category.cats))


def test_vcategory_repr():
    category = vCategory(["WORK", "PERSONAL"])
    category_repr = repr(category)
    assert category_repr == (
        "vCategory([vText(b'WORK'), vText(b'PERSONAL')], params=Parameters({}))"
    )


def test_vdate_rejects_invalid_calendar_date():
    with pytest.raises(ValueError, match="Wrong date format 20250230"):
        vDate.from_ical("20250230")


def test_vweekday_rejects_invalid_jcal_value():
    with pytest.raises(
        JCalParsingError,
        match="The value must be a valid weekday",
    ):
        vWeekday.parse_jcal_value("NOT-A-WEEKDAY")
