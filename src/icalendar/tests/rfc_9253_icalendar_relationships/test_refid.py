"""Test the REFID property."""

import pytest

from icalendar import Component


@pytest.fixture
def component():
    """Return a basic component for testing."""
    return Component()


def test_new_component_with_concept():
    """We can use new with just a string."""
    component = Component.new(refids="refid-1")
    assert len(component.refids) == 1
    assert component.refids[0] == "refid-1"
    assert isinstance(component.refids[0], str)


def test_delete_refids(component: Component):
    del component.refids
    component.refids = ["asd"]
    del component.refids
    assert component.refids is None


def test_delete_refids_with_none(component: Component):
    component.refids = ["123"]
    component.refids = None
    assert component.refids is None


def test_append_one_value_is_noop(component: Component):
    """Mutating the returned list is a no-op."""
    component.refids = ["ref1"]
    values = component.refids
    values.append("ref2")
    assert component.refids == ["ref1"]


def test_append_with_two_values_is_noop(component: Component):
    """Mutating the returned list is a no-op."""
    component.refids = ["ref1", "ref2"]
    values = component.refids
    values.append("ref3")
    assert component.refids == ["ref1", "ref2"]


def test_elements_are_str(component: Component):
    """Elements should be a plain str, not vText."""
    component.refids = ["ref1", "ref2"]
    assert all(type(x) is str for x in component.refids)
