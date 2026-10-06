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


def test_append_to_refids_on_new_component():
    """Issue #1722: Appending to list properties on new component persists."""
    comp = Component()
    comp.refids.append("refid-1")
    assert "REFID" in comp
    assert comp.refids == ["refid-1"]
    assert "refid-1" in comp.refids


def test_extend_and_insert_refids():
    """Extending and inserting into list properties persists in component storage."""
    comp = Component()
    comp.refids.extend(["ref-b", "ref-c"])
    comp.refids.insert(0, "ref-a")
    assert comp.refids == ["ref-a", "ref-b", "ref-c"]
    assert "REFID" in comp


def test_clear_and_remove_refids():
    """Clearing and removing all items cleanly unsets the property key."""
    comp = Component()
    comp.refids.extend(["ref-1", "ref-2"])
    comp.refids.remove("ref-1")
    assert comp.refids == ["ref-2"]
    assert "REFID" in comp
    comp.refids.remove("ref-2")
    assert comp.refids == []
    assert "REFID" not in comp

    comp2 = Component()
    comp2.refids.append("ref-temp")
    assert "REFID" in comp2
    comp2.refids.clear()
    assert comp2.refids == []
    assert "REFID" not in comp2


def test_pop_and_item_assignment_refids():
    """Popping and index mutation synchronize with component storage."""
    comp = Component()
    comp.refids.extend(["ref-1", "ref-2"])
    comp.refids[0] = "ref-updated"
    assert comp.refids == ["ref-updated", "ref-2"]

    val = comp.refids.pop()
    assert val == "ref-2"
    assert comp.refids == ["ref-updated"]
    assert "REFID" in comp

    del comp.refids[0]
    assert comp.refids == []
    assert "REFID" not in comp


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
