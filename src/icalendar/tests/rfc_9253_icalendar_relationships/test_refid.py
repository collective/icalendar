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
    assert component.refids == []


def test_delete_refids_with_none(component: Component):
    component.refids = ["123"]
    component.refids = None
    assert component.refids == []


def test_append_to_refids_on_new_component(component: Component):
    """Issue #1722: Appending to list properties on new component persists."""
    component.refids.append("refid-1")
    assert "REFID" in component
    assert component.refids == ["refid-1"]
    assert "refid-1" in component.refids


def test_multiple_property_list_views_stay_synchronized(component: Component):
    """Multiple PropertyListView references stay synchronized."""
    a = component.refids
    a.append("refid-sync")
    b = component.refids
    assert a == b
    assert list(a) == ["refid-sync"]


def test_extend_and_insert_refids(component: Component):
    """Extending and inserting into list properties persists in component storage."""
    component.refids.extend(["ref-b", "ref-c"])
    component.refids.insert(0, "ref-a")
    assert component.refids == ["ref-a", "ref-b", "ref-c"]
    assert "REFID" in component


def test_clear_and_remove_refids(component: Component):
    """Clearing and removing all items cleanly unsets the property key."""
    component.refids.extend(["ref-1", "ref-2"])
    component.refids.remove("ref-1")
    assert component.refids == ["ref-2"]
    assert "REFID" in component
    component.refids.remove("ref-2")
    assert component.refids == []
    assert "REFID" not in component

    comp2 = Component()
    comp2.refids.append("ref-temp")
    assert "REFID" in comp2
    comp2.refids.clear()
    assert comp2.refids == []
    assert "REFID" not in comp2


def test_pop_and_item_assignment_refids(component: Component):
    """Popping and index mutation synchronize with component storage."""
    component.refids.extend(["ref-1", "ref-2"])
    component.refids[0] = "ref-updated"
    assert component.refids == ["ref-updated", "ref-2"]

    val = component.refids.pop()
    assert val == "ref-2"
    assert component.refids == ["ref-updated"]
    assert "REFID" in component

    del component.refids[0]
    assert component.refids == []
    assert "REFID" not in component


def test_append_to_concepts_and_related_to():
    """Appending to concepts and related_to persists to component storage."""
    comp = Component()
    comp.concepts.append("https://example.com/concept1")
    assert "CONCEPT" in comp
    assert len(comp.concepts) == 1

    comp2 = Component()
    comp2.related_to.append("rel-001")
    assert "RELATED-TO" in comp2
    assert len(comp2.related_to) == 1


def test_set_refids_to_itself(component: Component):
    """Setting an attribute to its own value keeps the values."""
    component.refids = ["a", "b"]
    component.refids = component.refids
    assert component.refids == ["a", "b"]


def test_set_refids_to_value_of_other_attribute(component: Component):
    """Setting an attribute from another list attribute copies the values."""
    component.related_to = ["uid-1", "uid-2"]
    component.refids = component.related_to
    assert component.refids == ["uid-1", "uid-2"]
    assert component.related_to == ["uid-1", "uid-2"]


def test_set_refids_to_single_value_and_tuple(component: Component):
    component.refids = "a"
    assert component.refids == ["a"]
    component.refids = ("b", "c")
    assert component.refids == ["b", "c"]


def test_clear_removes_the_property(component: Component):
    component.refids = ["a"]
    component.refids.clear()
    assert "REFID" not in component
    assert component.refids == []


def test_views_compare_equal_and_not_equal_to_non_iterables(component: Component):
    """Views are equal to views with the same values, and not to other objects."""
    component.refids = ["a"]
    component.related_to = ["a"]
    assert component.refids == component.related_to
    assert component.refids != 1


def test_repr_of_view(component: Component):
    component.refids = ["a"]
    assert repr(component.refids).startswith("PropertyListView(")
