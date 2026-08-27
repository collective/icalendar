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
    ("own_names", "prop"),
    [
        (("DTSTAMP", "stamp"), Component.__dict__["DTSTAMP"]),
        (("CREATED", "created"), Component.__dict__["CREATED"]),
        (("LAST_MODIFIED", "last_modified"), Component.__dict__["LAST_MODIFIED"]),
    ],
)
def test_see_also_does_not_reference_the_property_itself(own_names, prop):
    """A timestamp property should point at the other two, not at itself."""
    _, _, see_also = prop.__doc__.partition("See also:")
    assert see_also, "no See also section found"
    for name in own_names:
        assert f":attr:`{name}`" not in see_also, (
            f"{own_names[0]} lists itself in its own See also section"
        )
