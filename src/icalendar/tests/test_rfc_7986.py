"""This tests additional attributes from :rfc:`7986`.

Some attributes are also available as X-... attributes.
They are also considered.
"""

import pytest

from icalendar import Calendar
from icalendar.prop import vText


@pytest.fixture()
def calendar() -> Calendar:
    """Empty calendar"""
    return Calendar()


param_name = pytest.mark.parametrize("name", ["Company Vacation Days", "Calendar Name"])
param_prop = pytest.mark.parametrize("prop", ["NAME", "X-WR-CALNAME"])


@param_prop
@param_name
def test_get_calendar_name(prop, name, calendar):
    """Get the name of the calendar."""
    calendar.add(prop, name)
    assert calendar.calendar_name == name


@param_name
def test_set_calendar_name(name, calendar):
    """Setting the name overrides the old attributes."""
    calendar.calendar_name = name
    assert calendar.calendar_name == name
    assert calendar["NAME"] == name


@param_name
@param_prop
def test_replace_name(name, prop, calendar):
    """Setting the name overrides the old attributes."""
    calendar[prop] = "Other Name"
    calendar.calendar_name = name
    assert calendar.calendar_name == name


@param_name
@param_prop
def test_del_name(name, calendar, prop):
    """Delete the name."""
    calendar.add(prop, name)
    del calendar.calendar_name
    assert calendar.calendar_name is None


def test_default_name(calendar):
    """We have no name by default."""
    assert calendar.calendar_name is None


@param_name
def test_setting_the_name_deletes_the_non_standard_attribute(calendar, name):
    """The default_attr is deleted when setting the name."""
    calendar["X-WR-CALNAME"] = name
    assert "X-WR-CALNAME" in calendar
    calendar.calendar_name = "other name"
    assert "X-WR-CALNAME" not in calendar


@param_name
@pytest.mark.parametrize("order", [1, 2])
def test_multiple_names_use_the_one_without_a_language(calendar, name, order):
    """Add several names and use the one without a language param."""
    if order == 1:
        calendar.add("NAME", name)
    calendar.add("NAME", vText("Kalendername", params={"LANGUAGE":"de"}))
    if order == 2:
        calendar.add("NAME", name)
    assert calendar.calendar_name == name


@param_name
def test_name_is_preferred(calendar, name):
    """NAME is more important that X-WR-CALNAME"""
    calendar.add("NAME", name)
    calendar.add("X-WR-CALNAME", "asd")
    assert calendar.calendar_name == name



# For description, we would use the same tests as name but we also use the
# same code, so it is alright.

param_color = pytest.mark.parametrize("desc", ["DESCRIPTION", "X-WR-CALDESC"])

@param_color
@param_name
def test_description(calendar, desc, name):
    """Get the value"""
    calendar.add(desc, name)
    assert calendar.calendar_description == name

# For color, we would use the same tests as name but we also use the
# same code, so it is alright.

param_color = pytest.mark.parametrize("color", ["COLOR", "X-APPLE-CALENDAR-COLOR"])

@param_color
@param_name
def test_color(calendar, color, name):
    """Get the value"""
    calendar.add(color, name)
    assert calendar.calendar_color == name
