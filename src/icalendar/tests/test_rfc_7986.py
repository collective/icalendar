"""This tests additional attributes from :rfc:`7986`.

Some attributes are also available as ``X-*`` attributes.
They are also considered.
"""
from __future__ import annotations

from typing import Union

import pytest

from icalendar import Calendar, Event, Journal, Todo
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



# For description, we would use the same tests as name, but we also use the
# same code, so it is all right.

param_color = pytest.mark.parametrize("desc", ["DESCRIPTION", "X-WR-CALDESC"])

@param_color
@param_name
def test_description(calendar, desc, name):
    """Get the value"""
    calendar.add(desc, name)
    assert calendar.description == name

# For color, we would use the same tests as name, but we also use the
# same code, so it is all right.

param_color = pytest.mark.parametrize("color_param", ["COLOR", "X-APPLE-CALENDAR-COLOR"])

@param_color
def test_get_calendar_color(calendar, color_param, color):
    """Get the value"""
    calendar.add(color_param, color)
    assert calendar.color == color

@param_color
def test_delete_calendar_color(calendar, color_param, color):
    """Delete the value"""
    calendar.add(color_param, color)
    del calendar.color
    assert calendar.color == ""
    assert color_param not in calendar

@param_color
def test_set_calendar_color(calendar, color_param, color):
    """Set the color and it replaces what is there."""
    calendar.add(color_param, "green")
    calendar.color = color
    assert calendar.color == color
    assert calendar["COLOR"] == color

def test_get_COLOR_first(calendar, color):
    """We prefer COLOR over X-APPLE-CALENDAR-COLOR"""
    calendar.add("COLOR", color)
    calendar.add("X-APPLE-CALENDAR-COLOR", "green")
    assert calendar.color == color

# The color of the event is a bit different
# It only appears once and does not have a backup.

@pytest.fixture(params=[Calendar, Event, Todo, Journal])
def color_component(request) -> Union[Calendar, Event, Todo, Journal]:
    """An empty component that should have a color attribute."""
    return request.param()

@pytest.fixture(params=["blue", "#123456"])
def color(request) -> str:
    """Return a color."""
    return request.param

def test_default_color(color_component: Union[Calendar, Event, Todo, Journal]):
    """There is no color by default."""
    assert color_component.color == ""

def test_set_the_color(color:str, color_component: Union[Calendar, Event, Todo, Journal]):
    """We set the value and get it."""
    color_component.color = color
    assert color_component.color == color
    assert color_component["COLOR"] == color

def test_replace_color(color:str, color_component: Union[Calendar, Event, Todo, Journal]):
    """Replace the color."""
    color_component.color = "blue"
    color_component.color = color
    assert color_component.color == color
    assert color_component["COLOR"] == color


def test_multiple_colors(color_component: Union[Calendar, Event, Todo, Journal]):
    """Add several colors and use the first one."""
    color_component.add("COLOR", "blue")
    color_component.add("COLOR", "green")
    assert color_component.color == "blue"


def test_delete_the_color(color_component: Union[Calendar, Event, Todo, Journal]):
    """Delete the color."""
    color_component.color = "blue"
    del color_component.color
    assert "COLOR" not in color_component
    assert color_component.color == ""


def test_set_if_multiple_colors(color: str, color_component: Union[Calendar, Event, Todo, Journal]):
    """Add several colors and use the first one."""
    color_component.add("COLOR", "blue")
    color_component.add("COLOR", "green")
    color_component.color = color
    assert color_component.color == color
