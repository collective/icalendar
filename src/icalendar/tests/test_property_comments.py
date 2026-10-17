"""Tests for PropertyListView with text properties and COMMENT property."""

from __future__ import annotations

import pytest

from icalendar import Component, Event
from icalendar.attr import PropertyListView
from icalendar.prop import vText


@pytest.fixture
def event() -> Event:
    """Return a fresh Event component."""
    return Event()


def test_comments_empty_by_default(event: Event):
    """Comments list is empty and COMMENT is not in component by default."""
    assert event.comments == []
    assert len(event.comments) == 0
    assert "COMMENT" not in event


def test_comments_append_persists_as_vtext(event: Event):
    """Appending to comments modifies component storage and converts to vText."""
    event.comments.append("First comment")
    assert "COMMENT" in event
    assert len(event.comments) == 1
    assert event.comments[0] == "First comment"
    assert isinstance(event.comments[0], vText)
    assert event.comments == ["First comment"]


def test_comments_multiple_append_and_extend(event: Event):
    """Multiple appends and extends persist in component."""
    event.comments.append("First")
    event.comments.append("Second")
    assert len(event.comments) == 2
    assert event.comments == ["First", "Second"]
    assert all(isinstance(c, vText) for c in event.comments)

    event.comments.extend(["Third", vText("Fourth")])
    assert len(event.comments) == 4
    assert event.comments == ["First", "Second", "Third", "Fourth"]
    assert all(isinstance(c, vText) for c in event.comments)


def test_comments_insert_and_setitem(event: Event):
    """Inserting and index assignment convert to vText and persist."""
    event.comments.extend(["one", "three"])
    event.comments.insert(1, "two")
    assert event.comments == ["one", "two", "three"]
    assert isinstance(event.comments[1], vText)

    event.comments[0] = "updated-one"
    assert event.comments == ["updated-one", "two", "three"]
    assert isinstance(event.comments[0], vText)


def test_comments_delitem_and_pop(event: Event):
    """Deleting items and popping from comments updates component."""
    event.comments.extend(["a", "b", "c"])
    del event.comments[1]
    assert event.comments == ["a", "c"]
    assert "COMMENT" in event

    popped = event.comments.pop()
    assert popped == "c"
    assert event.comments == ["a"]

    del event.comments[0]
    assert event.comments == []
    assert "COMMENT" not in event


def test_comments_clear(event: Event):
    """clear() removes all comments and unsets the COMMENT key."""
    event.comments.append("Temporary comment")
    assert "COMMENT" in event
    event.comments.clear()
    assert event.comments == []
    assert "COMMENT" not in event


def test_comments_replace_with_none_and_slice(event: Event):
    """Setting comments to None removes property; slice assignment converts values."""
    event.comments = ["c1", "c2"]
    assert len(event.comments) == 2
    event.comments[0:2] = ["new1", "new2"]
    assert event.comments == ["new1", "new2"]
    assert all(isinstance(c, vText) for c in event.comments)

    event.comments = None
    assert event.comments == []
    assert "COMMENT" not in event


def test_comments_serialization(event: Event):
    """Modifications to comments serialize cleanly into iCalendar format."""
    event.comments.append("First note")
    event.comments.append("Second note")
    ical = event.to_ical().decode()
    assert "COMMENT:First note\r\n" in ical
    assert "COMMENT:Second note\r\n" in ical


def test_property_list_view_for_text_factory():
    """PropertyListView.for_text creates a view converting strings to vText."""
    comp = Component()
    view = PropertyListView.for_text(comp, "X-CUSTOM-TEXT")
    view.append("custom value")
    assert comp["X-CUSTOM-TEXT"] == [vText(b"custom value")]
    assert isinstance(view[0], vText)


def test_comments_del_attribute(event: Event):
    """Deleting event.comments deletes the property from component."""
    event.comments = ["note1", "note2"]
    assert "COMMENT" in event
    del event.comments
    assert "COMMENT" not in event
    assert event.comments == []


def test_comments_setter_scalar_and_tuple(event: Event):
    """Setting comments to single string or tuple converts properly."""
    event.comments = "Single string"
    assert event.comments == ["Single string"]
    assert isinstance(event.comments[0], vText)

    event.comments = ("Tuple item 1", "Tuple item 2")
    assert event.comments == ["Tuple item 1", "Tuple item 2"]
    assert all(isinstance(c, vText) for c in event.comments)


def test_comments_across_other_components():
    """comments property works on Todo, Journal, Timezone, and Alarm components."""
    from icalendar.cal import Alarm, Journal, Timezone, Todo

    for cls in (Todo, Journal, Timezone, Alarm):
        comp = cls()
        assert comp.comments == []
        comp.comments.append(f"Note for {cls.__name__}")
        assert "COMMENT" in comp
        assert comp.comments == [f"Note for {cls.__name__}"]
        assert isinstance(comp.comments[0], vText)
        del comp.comments
        assert "COMMENT" not in comp
        assert comp.comments == []


def test_property_list_view_dict_and_fallback_converter():
    """PropertyListView with dict converter and fallback behavior."""
    comp = Component()
    view = PropertyListView(comp, "X-DICT-CONV", converter={str: vText})
    view.append("converted-str")
    view.append(42)
    assert isinstance(view[0], vText)
    assert view[1] == 42

    comp2 = Component()
    view2 = PropertyListView(comp2, "X-NO-CONV", converter=None)
    view2.append("raw-val")
    assert view2[0] == "raw-val"
    assert type(view2[0]) is str

    comp3 = Component()
    view3 = PropertyListView(comp3, "X-OTHER-CONV", converter="not-callable-or-dict")
    view3.append("fallback-val")
    assert view3[0] == "fallback-val"

