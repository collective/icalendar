"""This tests the creation of new components.

To aid creating valid calendars with a few lines of code, the components
receive a new() classmethod.
This method MUST use property setters to set the properties defined in the keywords.

New keywords can be added over time.

See https://github.com/collective/icalendar/issues/843
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional

import pytest

from icalendar.cal import Alarm, Event, Journal, Todo
from icalendar.cal.component import Component

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

param_summary_components = pytest.mark.parametrize(
    "component", [Event, Todo, Alarm, Journal]
)
param_description_components = pytest.mark.parametrize(
    "component", [Event, Todo, Alarm, Journal]
)


@param_summary_components
def test_summary_default(component):
    """Test the summary property default."""
    c = component()
    assert c.summary is None


@param_description_components
def test_description_default(component):
    """Test the summary property default."""
    c = component()
    assert c.description is None


@param_summary_components
def test_summary_delete(component):
    """Test the summary property default."""
    c = component()
    c.summary = "alksdj"
    del c.summary
    assert c.summary is None
    del c.summary
    assert c.summary is None


@param_description_components
def test_description_delete(component):
    """Test the summary property default."""
    c = component()
    c.description = "alksdj"
    del c.description
    assert c.description is None
    del c.description
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


def new_journal_description(description) -> Journal:
    """use new()"""
    return Journal.new(description=description)


def set_journal_description(description) -> Journal:
    """Set the description"""
    journal = Journal()
    journal.descriptions = description
    return journal


@pytest.mark.parametrize(
    ("description", "expected_description"),
    [
        (None, []),
        ([], []),
        ("one description", ["one description"]),
        (("desc12", "desc23"), ["desc12", "desc23"]),
    ],
)
@pytest.mark.parametrize(
    "get_journal", [new_journal_description, set_journal_description]
)
def test_journal_description_is_a_list(get_journal, description, expected_description):
    """A jounal entry can have several descriptions."""
    journal = get_journal(description)
    assert journal.descriptions == expected_description
    if not description:
        assert "DESCRIPTION" not in journal
    else:
        assert "DESCRIPTION" in journal


def test_multiple_descriptions_are_concatenated():
    """For compatibility we also provide the description method that concatenates descriptions."""
    journal = Journal.new(description=("one description", "two descriptions"))
    assert journal.description == "one description\r\n\r\ntwo descriptions"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2023, 10, 21), datetime(2023, 10, 21, tzinfo=timezone.utc)),
        (datetime(2023, 10, 22), datetime(2023, 10, 22, tzinfo=timezone.utc)),
        (
            datetime(2023, 10, 23, 12, 30, tzinfo=timezone.utc),
            datetime(2023, 10, 23, 12, 30, tzinfo=ZoneInfo("UTC")),
        ),
        (
            datetime(2023, 10, 24, 21, 0, 1, tzinfo=timezone(timedelta(hours=1))),
            datetime(2023, 10, 24, 20, 0, 1, tzinfo=ZoneInfo("UTC")),
        ),
    ],
)
def test_dtstamp_becomes_utc(value, expected):
    """We set and get the dtstamp."""
    component = Component()
    component.DTSTAMP = value
    assert component.DTSTAMP == expected
