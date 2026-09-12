"""Tests for validating integer properties with a minimum value.

See https://github.com/collective/icalendar/issues/1594
"""

from datetime import timedelta

import pytest

from icalendar import Alarm, Event, InvalidCalendar
from icalendar.attr import single_int_property
from icalendar.cal.component import Component


class NumberComponent(Component):
    """A component with a single integer property that has a minimum."""

    name = "X-NUMBER"
    number = single_int_property("NUMBER", 0, "A number", min_value=5)


@pytest.mark.parametrize("value", [0, 1, 10])
def test_set_non_negative_value(value):
    """Setting a non-negative value works."""
    alarm = Alarm()
    alarm.REPEAT = value
    assert alarm.REPEAT == value


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (-1, "REPEAT must be >= 0, got -1"),
        (-10, "REPEAT must be >= 0, got -10"),
    ],
)
def test_set_negative_value_raises(value, message):
    """Setting a negative value raises an error with the correct message."""
    alarm = Alarm()
    with pytest.raises(InvalidCalendar, match=message):
        alarm.REPEAT = value


@pytest.mark.parametrize("value", ["asd", 1.5, object()])
def test_set_non_integer_raises(value):
    """Setting a non-integer value raises a TypeError."""
    alarm = Alarm()
    with pytest.raises(TypeError, match="REPEAT must be an int, got"):
        alarm.REPEAT = value


@pytest.mark.parametrize("value", [True, False])
def test_set_bool_raises(value):
    """Booleans are rejected too, even though bool is a subclass of int."""
    alarm = Alarm()
    with pytest.raises(TypeError, match="REPEAT must be an int, got"):
        alarm.REPEAT = value


def test_set_non_integer_raises_for_sequence():
    """The same TypeError is raised for other integer properties."""
    event = Event()
    with pytest.raises(TypeError, match="SEQUENCE must be an int, got"):
        event.sequence = "1"


def test_set_none_deletes():
    """Setting None deletes the property, like before."""
    alarm = Alarm()
    alarm.REPEAT = 3
    alarm.REPEAT = None
    assert alarm.REPEAT == 0


def test_custom_min_value_boundary():
    """Exactly min_value is accepted."""
    component = NumberComponent()
    component.number = 5
    assert component.number == 5


def test_custom_min_value_below_boundary_raises():
    """One below min_value raises with the correct message."""
    component = NumberComponent()
    with pytest.raises(InvalidCalendar, match="NUMBER must be >= 5, got 4"):
        component.number = 4


@pytest.mark.parametrize("min_value", [0, 5, 10])
def test_different_min_values(min_value):
    """Different minimal values are enforced at their boundary."""
    prop = single_int_property("VALUE", 0, "A value", min_value=min_value)
    component = type("C", (Component,), {"name": "X-VALUE", "value": prop})()
    component.value = min_value
    assert component.value == min_value
    with pytest.raises(InvalidCalendar, match=f"VALUE must be >= {min_value}"):
        component.value = min_value - 1


def test_lowercase_repeat_validation():
    """The lowercase repeat attribute validates too."""
    alarm = Alarm()
    alarm.repeat = 2
    assert alarm.repeat == 2
    with pytest.raises(InvalidCalendar, match="REPEAT must be >= 0"):
        alarm.repeat = -1


def test_sequence_validation():
    """The sequence attribute validates too."""
    event = Event()
    event.sequence = 3
    assert event.sequence == 3
    with pytest.raises(InvalidCalendar, match="SEQUENCE must be >= 0"):
        event.sequence = -1


def test_priority_validation():
    """The priority attribute validates too."""
    event = Event()
    event.priority = 5
    assert event.priority == 5
    with pytest.raises(InvalidCalendar, match="PRIORITY must be >= 0"):
        event.priority = -1


def test_factory_methods_reject_negative_repeat():
    """Factory methods reject a negative repeat."""
    with pytest.raises(InvalidCalendar, match="REPEAT must be >= 0"):
        Alarm.new_display(
            "desc",
            timedelta(minutes=-5),
            duration=timedelta(minutes=1),
            repeat=-1,
        )
