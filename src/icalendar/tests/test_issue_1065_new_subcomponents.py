"""Tests for issue #1065: new() subcomponents parameter."""

import pytest

from icalendar import (
    Availability,
    Calendar,
    Component,
    Event,
    Timezone,
    Todo,
)


def _make_child() -> Component:
    """Create a minimal child component."""
    child = Component()
    child["X-TEST"] = "value"
    return child


# Classes that accept subcomponents in new(), with any required extra kwargs.
CLASSES_WITH_NEW = [
    pytest.param(Component, {}, id="Component"),
    pytest.param(Event, {"summary": "Test"}, id="Event"),
    pytest.param(Todo, {"summary": "Test"}, id="Todo"),
    pytest.param(Calendar, {}, id="Calendar"),
    pytest.param(Timezone, {}, id="Timezone"),
    pytest.param(Availability, {}, id="Availability"),
]


@pytest.mark.parametrize(("cls", "kwargs"), CLASSES_WITH_NEW)
def test_new_with_subcomponents(cls, kwargs):
    child = _make_child()
    obj = cls.new(**kwargs, subcomponents=[child])
    assert len(obj.subcomponents) == 1
    assert obj.subcomponents[0] is child


@pytest.mark.parametrize(("cls", "kwargs"), CLASSES_WITH_NEW)
def test_new_without_subcomponents(cls, kwargs):
    obj = cls.new(**kwargs)
    assert obj.subcomponents == []


@pytest.mark.parametrize(("cls", "kwargs"), CLASSES_WITH_NEW)
def test_subcomponents_list_identity(cls, kwargs):
    child = _make_child()
    original_list = [child]
    obj = cls.new(**kwargs, subcomponents=original_list)
    assert obj.subcomponents is original_list


@pytest.mark.parametrize(("cls", "kwargs"), CLASSES_WITH_NEW)
def test_subcomponents_tuple_becomes_list(cls, kwargs):
    child = _make_child()
    obj = cls.new(**kwargs, subcomponents=(child,))
    assert isinstance(obj.subcomponents, list)
    assert len(obj.subcomponents) == 1
    assert obj.subcomponents[0] is child
