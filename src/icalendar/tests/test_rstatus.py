"""This tests the REQUEST-STATUS property.

See
- https://github.com/collective/icalendar/issues/1666
- https://www.rfc-editor.org/rfc/rfc5545#section-3.8.8.3
"""

import pytest

from icalendar.cal.event import Event
from icalendar.cal.free_busy import FreeBusy
from icalendar.cal.journal import Journal
from icalendar.cal.todo import Todo

ETJF = Event | Todo | Journal | FreeBusy


@pytest.fixture(params=[Event, Todo, Journal, FreeBusy])
def component(request):
    """An empty component with possible rstatus."""
    return request.param()


def test_no_rstatus_at_creation(component: ETJF):
    """An empty component has no rstatus."""
    assert "RSTATUS" not in component
    assert component.rstatus == []


def test_add_one_rstatus(component: ETJF):
    """Add one rstatus."""
    component.add("rstatus", "2.0;Success")
    assert component.rstatus == ["2.0;Success"]


def test_add_multiple_rstatus(component: ETJF):
    """Add rstatus."""
    component.add("rstatus", ["2.0;Success", "3.1;Invalid property value"])
    assert component.rstatus == ["2.0;Success", "3.1;Invalid property value"]


def test_set_rstatus(component: ETJF):
    """Set rstatus."""
    component.rstatus = ["2.0;Success", "3.1;Invalid property value"]
    assert component.rstatus == ["2.0;Success", "3.1;Invalid property value"]


def test_delete_rstatus(component: ETJF):
    """Delete rstatus."""
    component.rstatus = ["2.0;Success"]
    del component.rstatus
    assert "RSTATUS" not in component
    assert component.rstatus == []


def test_rstatus_roundtrip(component: ETJF):
    """The rstatus survives a roundtrip."""
    component.rstatus = ["2.0;Success", "3.1;Invalid property value"]
    ics = component.to_ical()
    parsed = component.__class__.from_ical(ics)
    assert parsed.rstatus == ["2.0;Success", "3.1;Invalid property value"]


def test_new_with_rstatus(component: ETJF):
    """We can use new with rstatus."""
    component = component.__class__.new(rstatus="2.0;Success")
    assert component.rstatus == ["2.0;Success"]
