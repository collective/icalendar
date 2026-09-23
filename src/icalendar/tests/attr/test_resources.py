"""This tests the RESOURCES property.

See
- https://github.com/collective/icalendar/issues/1667
- https://www.rfc-editor.org/rfc/rfc5545#section-3.8.1.10
"""

import pytest

from icalendar.cal.event import Event
from icalendar.cal.todo import Todo

ET = Event | Todo


@pytest.fixture(params=[Event, Todo])
def component(request):
    """An empty component with possible resources."""
    return request.param()


def test_no_resources_at_creation(component: ET):
    """An empty component has no resources."""
    assert "RESOURCES" not in component
    assert component.RESOURCES is None


def test_add_one_resource(component: ET):
    """Add one resource."""
    component.add("RESOURCES", "EASEL")
    assert component.RESOURCES == ["EASEL"]


def test_add_multiple_resources(component: ET):
    """Add several resources."""
    component.add("RESOURCES", ["EASEL", "PROJECTOR", "VCR"])
    assert component.RESOURCES == ["EASEL", "PROJECTOR", "VCR"]


def test_successive_adds(component: ET):
    """Successive adds accumulate."""
    component.add("RESOURCES", "EASEL")
    component.add("RESOURCES", "TELEGRAPH")
    assert component.RESOURCES == ["EASEL", "TELEGRAPH"]


def test_set_resources(component: ET):
    """Set resources."""
    component.RESOURCES = ["EASEL", "PROJECTOR", "VCR"]
    assert component.RESOURCES == ["EASEL", "PROJECTOR", "VCR"]


def test_delete_resources(component: ET):
    """Delete resources."""
    component.RESOURCES = ["EASEL"]
    del component.RESOURCES
    assert "RESOURCES" not in component
    assert component.RESOURCES is None


def test_delete_by_index(component: ET):
    """Deleting from the returned list does not
    modify the component; reassigns to make the
    changes stick."""
    component.RESOURCES = ["EASEL", "TELEGRAPH"]
    value = component.RESOURCES
    del value[0]
    assert component.RESOURCES == ["EASEL", "TELEGRAPH"]
    component.RESOURCES = value
    assert component.RESOURCES == ["TELEGRAPH"]


def test_resources_roundtrip(component: ET):
    """The resources survive a roundtrip."""
    component.RESOURCES = ["EASEL", "PROJECTOR", "VCR"]
    ics = component.to_ical()
    parsed = component.__class__.from_ical(ics)
    assert parsed.RESOURCES == ["EASEL", "PROJECTOR", "VCR"]


def test_new_with_resources(component: ET):
    """We can use new with resources."""
    component = component.__class__.new(resources="EASEL")
    assert component.RESOURCES == ["EASEL"]
