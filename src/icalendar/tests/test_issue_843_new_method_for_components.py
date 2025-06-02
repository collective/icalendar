"""This tests the creation of new components.

To aid creating valid calendars with a few lines of code, the components
receive a new() classmethod.
This method MUST use property setters to set the properties defined in the keywords.

New keywords can be added over time.

See https://github.com/collective/icalendar/issues/843
"""

from __future__ import annotations

import itertools
import traceback
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Optional

import pytest

from icalendar import (
    Alarm,
    Availability,
    Available,
    Calendar,
    Component,
    Event,
    FreeBusy,
    Journal,
    Todo,
)
from icalendar.enums import BUSYTYPE

from .conftest import NOW_UTC, UID_DEFAULT

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore  # noqa: PGH003


# Test parametrization

param_summary_components = pytest.mark.parametrize(
    "component", [Event, Todo, Alarm, Journal, Available, Availability]
)
param_description_components = pytest.mark.parametrize(
    "component", [Event, Todo, Alarm, Journal, Available, Availability]
)
COMPONENTS_DTSTAMP = {
    Component,
    Event,
    Journal,
    Todo,
    FreeBusy,
    Available,
    Availability,
}
COMPONENTS_DTSTAMP_AUTOMATIC = {Event, Journal, Todo, FreeBusy, Available, Availability}
COMPONENTS_UID_AUTOMATIC = {Event, Todo, Journal, Available, Availability}
COMPONENTS_UID = {Event, Todo, Journal, Alarm, Calendar, Available, Availability}
COMPONENTS_SEQUENCE = {Event, Todo, Journal, Availability}
COMPONENTS_CATEGORIES = {Event, Journal, Todo, Calendar, Availability, Available}
COMPONENTS_ORGANIZER = {Availability, Event, FreeBusy, Journal, Todo}
COMPONENTS_LOCATION = {Availability, Available, Event, Todo}
COMPONENTS_URL = {Availability, Event, Todo, Journal, FreeBusy}
COMPONENTS_BUSYTYPE = {Availability}
COMPONENTS_DESCRIPTION = {Event, Todo, Journal, Alarm, Available, Availability}
COMPONENTS_SUMMARY = {Event, Todo, Journal, Alarm, Available, Availability}


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
def test_journal_description_is_a_list(
    get_journal: Callable[..., Journal], description, expected_description
):
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


def component_setter(
    component_class: type[Component], property_name: str, value: Any
) -> Component:
    """We set the value of the component's attribute."""
    component = component_class()
    try:
        setattr(component, property_name, value)
    except TypeError:
        # we show the exception in case the test fails for easier debug
        traceback.print_exc()
        pytest.skip("Cannot set value")
    return component


def component_with_new(
    component_class: type[Component], property_name: str, value: Any
) -> Component:
    """Use new() to create the component."""
    kw = {property_name.lower(): value}
    return component_class.new(**kw)


def assert_component_attribute_has_value(
    component: Component, property_name: str, expected_value: Any, message
):
    """Make  sure that a component's attribute has a value."""
    actual_value = getattr(component, property_name)
    assert actual_value == expected_value, (
        f"The attribute {property_name} of {component} "
        f"should be {expected_value!r} but got {actual_value!r}.\n{message}"
    )


automatic_time_test_cases = list(
    itertools.chain.from_iterable(
        [
            (
                COMPONENTS_DTSTAMP,
                property_name,
                key,
                date(2023, 10, 21),
                datetime(2023, 10, 21, tzinfo=timezone.utc),
                True,
                f"{key} becomes a UTC value",
            ),
            (
                COMPONENTS_DTSTAMP,
                property_name,
                key,
                datetime(2023, 10, 22),
                datetime(2023, 10, 22, tzinfo=timezone.utc),
                True,
                f"{key} becomes a UTC value",
            ),
            (
                COMPONENTS_DTSTAMP,
                property_name,
                key,
                datetime(2023, 10, 23, 12, 30, tzinfo=timezone.utc),
                datetime(2023, 10, 23, 12, 30, tzinfo=ZoneInfo("UTC")),
                True,
                f"{key} becomes a UTC value",
            ),
            (
                COMPONENTS_DTSTAMP,
                property_name,
                key,
                datetime(2023, 10, 24, 21, 0, 1, tzinfo=timezone(timedelta(hours=1))),
                datetime(2023, 10, 24, 20, 0, 1, tzinfo=ZoneInfo("UTC")),
                True,
                f"{key} becomes a UTC value",
            ),
            (
                COMPONENTS_DTSTAMP_AUTOMATIC,
                property_name,
                key,
                None,
                NOW_UTC,
                True,
                f"we use the current time to create a datetime for {key}",
            ),
            (
                COMPONENTS_DTSTAMP - COMPONENTS_DTSTAMP_AUTOMATIC,
                property_name,
                key,
                None,
                None,
                False,
                f"{key} is not automatically set",
            ),
        ]
        for property_name, key in (
            ("DTSTAMP", "DTSTAMP"),
            ("created", "CREATED"),
            ("LAST_MODIFIED", "LAST-MODIFIED"),
        )
    )
)


@pytest.mark.parametrize(
    (
        "component_classes",
        "property_name",
        "key",
        "initial_value",
        "expected_value",
        "key_present",
        "message",
    ),
    automatic_time_test_cases
    + [
        (
            COMPONENTS_UID,
            "uid",
            "uid",
            "test UID",
            "test UID",
            True,
            "Set the UID property",
        ),
        (
            COMPONENTS_UID_AUTOMATIC,
            "uid",
            "uid",
            None,
            UID_DEFAULT,
            True,
            "Set the UID property by default for these components",
        ),
        (
            COMPONENTS_UID - COMPONENTS_UID_AUTOMATIC,
            "uid",
            "uid",
            None,
            "",
            False,
            "UID is not automatically set",
        ),
        (
            {Event, Todo, Journal, Availability, Available},  # TODO: FreeBusy
            "start",
            "dtstart",
            datetime(2023, 10, 24, 21, 0, 1, tzinfo=ZoneInfo("Europe/Berlin")),
            datetime(2023, 10, 24, 21, 0, 1, tzinfo=ZoneInfo("Europe/Berlin")),
            True,
            "set the start",
        ),
        (
            {Event, Available},  # TODO: FreeBusy
            "end",
            "dtend",
            datetime(2023, 10, 24, 22, 0, 1, tzinfo=ZoneInfo("Europe/Berlin")),
            datetime(2023, 10, 24, 22, 0, 1, tzinfo=ZoneInfo("Europe/Berlin")),
            True,
            "set the end",
        ),
        (
            {Todo},
            "end",
            "due",
            datetime(2023, 10, 24, 22, 0, 1, tzinfo=ZoneInfo("Europe/Berlin")),
            datetime(2023, 10, 24, 22, 0, 1, tzinfo=ZoneInfo("Europe/Berlin")),
            True,
            "set the end",
        ),
        (
            {Todo, Event, Calendar, Journal},
            "color",
            "color",
            "red",
            "red",
            True,
            "set the color",
        ),
        (
            COMPONENTS_SEQUENCE,
            "sequence",
            "SEQUENCE",
            1,
            1,
            True,
            "set the sequence",
        ),
        (
            COMPONENTS_SEQUENCE,
            "sequence",
            "SEQUENCE",
            None,
            0,
            False,
            "get the default the sequence",
        ),
        (
            COMPONENTS_CATEGORIES,
            "categories",
            "CATEGORIES",
            ["cat1", "cat2"],
            ["cat1", "cat2"],
            True,
            "set the categories",
        ),
        (
            COMPONENTS_CATEGORIES,
            "categories",
            "CATEGORIES",
            (),
            [],
            False,
            "categories are absent",
        ),
        (
            COMPONENTS_ORGANIZER,
            "organizer",
            "ORGANIZER",
            "mailto:bernard@example.com",
            "mailto:bernard@example.com",
            True,
            "set the organizer",
        ),
        (
            COMPONENTS_ORGANIZER,
            "organizer",
            "ORGANIZER",
            None,
            None,
            False,
            "no organizer by default",
        ),
        (
            COMPONENTS_LOCATION,
            "location",
            "LOCATION",
            "Berlin",
            "Berlin",
            True,
            "set the location",
        ),
        (
            COMPONENTS_LOCATION,
            "location",
            "LOCATION",
            None,
            None,
            False,
            "no location by default",
        ),
        (
            COMPONENTS_URL,
            "url",
            "URL",
            "https://icalendar.readthedocs.io/",
            "https://icalendar.readthedocs.io/",
            True,
            "set the url",
        ),
        (
            COMPONENTS_URL,
            "url",
            "URL",
            None,
            "",
            False,
            "no url by default",
        ),
        (
            COMPONENTS_BUSYTYPE,
            "busy_type",
            "BUSYTYPE",
            BUSYTYPE.BUSY,
            BUSYTYPE.BUSY,
            True,
            "set the url",
        ),
        (
            COMPONENTS_BUSYTYPE,
            "busy_type",
            "BUSYTYPE",
            None,
            BUSYTYPE.BUSY_UNAVAILABLE,
            False,
            "default busy type",
        ),
        (
            COMPONENTS_DESCRIPTION,
            "description",
            "DESCRIPTION",
            "This describes the component a bit more in detail.",
            "This describes the component a bit more in detail.",
            True,
            "set the description",
        ),
        (
            COMPONENTS_DESCRIPTION,
            "description",
            "DESCRIPTION",
            None,
            None,
            False,
            "no description by default",
        ),
        (
            COMPONENTS_SUMMARY,
            "summary",
            "SUMMARY",
            "component summary",
            "component summary",
            True,
            "set the summary",
        ),
        (
            COMPONENTS_SUMMARY,
            "summary",
            "SUMMARY",
            None,
            None,
            False,
            "no summary by default",
        ),
    ],
)
@pytest.mark.parametrize(
    "create_component_with_property", [component_setter, component_with_new]
)
def test_properties_and_new(
    create_component_with_property,
    component_classes,
    property_name,
    initial_value,
    expected_value,
    key_present,
    key,
    message,
):
    """We set and get the dtstamp."""
    for component_class in component_classes:
        component = create_component_with_property(
            component_class, property_name, initial_value
        )
        if (
            create_component_with_property is component_with_new
            or initial_value is not None
        ):
            assert (key in component) == key_present, message
            # the setter does not create default values
            # so we only check it if present
            assert_component_attribute_has_value(
                component, property_name, expected_value, message
            )
