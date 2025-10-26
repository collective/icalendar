"""Tests for icalendar relationships as per RFC 9253."""

import pytest

from icalendar import (
    Alarm,
    Availability,
    Available,
    Calendar,
    Event,
    FreeBusy,
    Journal,
    Timezone,
    TimezoneDaylight,
    TimezoneStandard,
    Todo,
)
from icalendar.prop import vUri


@pytest.fixture(
    params=(
        Alarm,
        Availability,
        Available,
        Calendar,
        Event,
        FreeBusy,
        Journal,
        Timezone,
        TimezoneDaylight,
        TimezoneStandard,
        Todo,
    )
)
def link_component_class(request):
    """The classes to test.

    rfc:`9253`::

        Conformance: Link: This property can be specified zero or
        more times in any iCalendar component.

    """
    return request.param


@pytest.fixture(
    params=[
        [],
        [vUri("https://example.com/resource1")],
    ]
)
def links(request, LABEL, LANGUAGE, LINKREL, FMTTYPE):  # noqa: N803
    """Generate a list of links that can be used."""


def test_no_links_by_default(link_component):
    """By default, components have no LINK properties."""
    assert "LINK" not in link_component
    assert link_component.links == []
