"""Properties must document themselves, at their call site.

These guard the docstrings built by
:func:`~icalendar.attr.single_utc_property`, which used to prepend a sentence
generated from the property name. That prefix hid the property's own summary
line from the reference index and repeated text the call sites already stated,
and it turned a copied caller docstring into a wrong one: ``DTEND`` inherited
``DTSTART``'s "Start of the component." and was documented as the start of the
component.

Part of https://github.com/collective/icalendar/issues/1650
"""

from datetime import datetime, timezone

import pytest

from icalendar.cal import Alarm, Availability, Available, Component, Event

#: iCalendar property name -> property object, as attached to its class
UTC_PROPERTIES = {
    "DTSTAMP": Component.__dict__["DTSTAMP"],
    "CREATED": Component.__dict__["CREATED"],
    "LAST_MODIFIED": Component.__dict__["LAST_MODIFIED"],
    "ACKNOWLEDGED": Alarm.__dict__["ACKNOWLEDGED"],
    "X-MOZ-SNOOZE-TIME": Event.__dict__["X_MOZ_SNOOZE_TIME"],
    "X-MOZ-LASTACK": Event.__dict__["X_MOZ_LASTACK"],
}


@pytest.mark.parametrize(("name", "prop"), list(UTC_PROPERTIES.items()))
def test_docstring_is_not_composed_from_the_property_name(name, prop):
    """The generated sentence must not appear in any property docstring."""
    assert prop.__doc__ is not None, f"{name} has no docstring"
    assert "property with all values converted" not in prop.__doc__


@pytest.mark.parametrize(
    ("component", "prop"),
    [
        pytest.param(
            Availability, Availability.__dict__["DTSTART"], id="Avail-DTSTART"
        ),
        pytest.param(Availability, Availability.__dict__["DTEND"], id="Avail-DTEND"),
        pytest.param(Available, Available.__dict__["DTSTART"], id="Available-DTSTART"),
        pytest.param(Available, Available.__dict__["DTEND"], id="Available-DTEND"),
    ],
)
def test_timezone_property_summary_names_the_right_boundary(component, prop):
    """``DTEND`` must describe the end, not repeat ``DTSTART``'s summary."""
    doc = prop.__doc__
    assert doc, f"{component.__name__}.{prop} has no docstring"
    summary = doc.splitlines()[0].strip()
    attr_name = next(n for n in ("DTSTART", "DTEND") if component.__dict__[n] is prop)
    expected = (
        "Start of the component" if attr_name == "DTSTART" else "End of the component"
    )
    assert summary.startswith(expected), (
        f"{component.__name__}.{attr_name} is documented as {summary!r}"
    )


@pytest.mark.parametrize(
    ("name", "prop"),
    [
        ("DTSTAMP", Component.__dict__["DTSTAMP"]),
        ("CREATED", Component.__dict__["CREATED"]),
        ("LAST_MODIFIED", Component.__dict__["LAST_MODIFIED"]),
    ],
)
def test_see_also_is_not_self_referential(name, prop):
    """See also may list uppercase and lowercase counterparts, but not itself.

    Uppercase and lowercase properties behave differently, so they may refer to
    each other's counterparts; a property must not refer to itself.
    """
    _, _, see_also = prop.__doc__.partition("See also:")
    assert see_also, f"{name} has no See also section"
    assert f":attr:`{name}`" not in see_also, f"{name} See also is self-referential"
    for lowercase in ("created", "stamp", "last_modified"):
        assert f":attr:`{lowercase}`" in see_also, (
            f"{name} See also should list the :attr:`{lowercase}` counterpart"
        )


def test_stamp_is_a_distinct_accessor_with_a_deleter():
    """stamp is no longer the same property object as DTSTAMP, and deleting it
    removes DTSTAMP, preserving the functionality that existed before the alias
    was removed (review 2026-08-30).
    """
    assert Component.__dict__["stamp"] is not Component.__dict__["DTSTAMP"]
    assert Component.__dict__["stamp"].fdel is not None
    event = Event()
    event.stamp = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    del event.stamp
    assert event.DTSTAMP is None
