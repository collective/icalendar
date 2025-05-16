"""This tests the creation of new components.

To aid creating valid calendars with a few lines of code, the components
receive a new() classmethod.
This method MUST use property setters to set the properties defined in the keywords.

New keywords can be added over time.

See https://github.com/collective/icalendar/issues/843
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.cal.event import Event
from icalendar.cal.journal import Journal
from icalendar.cal.todo import Todo

if TYPE_CHECKING:
    from icalendar.cal.component import Component

param_summary_components = pytest.mark.parametrize(
    "component", [Event, Todo, Alarm, Journal]
)
param_description_components = pytest.mark.parametrize(
    "component", [Event, Todo, Alarm]
)


@param_summary_components
def test_summary_default(component):
    """Test the summary property default."""
    c = component()
    assert c.summary is None
    assert c.description is None


param_summary = pytest.mark.parametrize(
    "summary", ["akshdkjahskjdhas", "This is a more\ncomplex summary.", None]
)
param_description = pytest.mark.parametrize(
    "description", ["akshdkjahskjdhas", "This is a more\ncomplex summary.", None]
)


def assert_summary_equals(component: Component, summary: Optional[str]):
    """Check this is the summary."""
    assert_property_equals(component, "summary", summary)


def assert_description_equals(component: Component, summary: Optional[str]):
    """Check this is the summary."""
    assert_property_equals(component, "description", summary)


def assert_property_equals(component: Component, name: str, text: Optional[str]):
    """Check the property."""
    assert getattr(component, name.lower()) == text
    if text is None:
        assert name.upper() not in component
    else:
        assert component[name.upper()] == text


@param_summary_components
@param_summary
def test_set_summary(component, summary):
    """Test the summary property default."""
    c = component()
    c.summary = summary
    assert_summary_equals(c, summary)


@param_summary_components
@param_summary
def test_new_with_summary(component, summary):
    """Test the summary property default."""
    assert_summary_equals(component.new(summary=summary), summary)


@param_description_components
@param_description
def test_set_description(component, description):
    """Test the description property default."""
    c = component()
    c.description = description
    assert_description_equals(c, description)


@param_description_components
@param_description
def test_new_with_description(component, description):
    """Test the description property default."""
    assert_description_equals(component.new(description=description), description)
