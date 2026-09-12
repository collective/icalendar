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
    """An empty component with possible request status."""
    return request.param()


def test_no_request_status_at_creation(component: ETJF):
    """An empty component has no request status."""
    assert "REQUEST-STATUS" not in component
    assert component.REQUEST_STATUS == []


def test_add_one_request_status(component: ETJF):
    """Add one request status."""
    component.add("REQUEST-STATUS", "2.0;Success")
    assert component.REQUEST_STATUS == ["2.0;Success"]


def test_add_multiple_request_status(component: ETJF):
    """Add request status."""
    component.add("REQUEST-STATUS", ["2.0;Success", "3.1;Invalid property value"])
    assert component.REQUEST_STATUS == ["2.0;Success", "3.1;Invalid property value"]


def test_set_request_status(component: ETJF):
    """Set request status."""
    component.REQUEST_STATUS = ["2.0;Success", "3.1;Invalid property value"]
    assert component.REQUEST_STATUS == ["2.0;Success", "3.1;Invalid property value"]


def test_delete_request_status(component: ETJF):
    """Delete request status."""
    component.REQUEST_STATUS = ["2.0;Success"]
    del component.REQUEST_STATUS
    assert "REQUEST-STATUS" not in component
    assert component.REQUEST_STATUS == []


def test_request_status_roundtrip(component: ETJF):
    """The request status survives a roundtrip."""
    component.REQUEST_STATUS = ["2.0;Success", "3.1;Invalid property value"]
    ics = component.to_ical()
    parsed = component.__class__.from_ical(ics)
    assert parsed.REQUEST_STATUS == ["2.0;Success", "3.1;Invalid property value"]


def test_new_with_request_status(component: ETJF):
    """We can use new with request status."""
    component = component.__class__.new(request_status="2.0;Success")
    assert component.REQUEST_STATUS == ["2.0;Success"]
