"""Test component to xcal serialization."""

from xml.etree.ElementTree import Element, tostring

import pytest

from icalendar.cal.component import Component


def _xcal(component: Component) -> Element:
    """Return the xCal of a component."""
    e = Element("vcalendar")
    component.to_xcal(e)
    print(tostring(e, method="xml").decode())
    assert len(e) == 1
    return e[0]


def test_component_to_xcal_uses_component_name(component):
    """The name is lowercase, same as rfc 5545"""
    e = _xcal(component)
    assert e.tag == component.name.lower()


def test_empty_component(component):
    """Empty component without children."""
    e = _xcal(component)
    assert len(e) == 0


def test_adding_a_property(component):
    """Test that adding a property turns up."""
    component.add("comment", "this is a comment")
    e = _xcal(component)
    assert len(e) == 1
    props = e[0]
    assert props.tag == "properties"
    assert len(props) == 1
    comment = props[0]
    assert comment.tag == "comment"
    assert len(comment) == 1
    assert comment[0].tag == "text"
    assert comment[0].text == "this is a comment"


def test_component_without_name_to_ical_yields_error():
    c = Component()
    assert c.name is None
    with pytest.raises(ValueError) as error:
        c.to_ical()
    assert error.value.args == ("This component needs a name for serialization.", c)
    with pytest.raises(ValueError) as error:
        c.to_jcal()
    assert error.value.args == ("This component needs a name for serialization.", c)
    with pytest.raises(ValueError) as error:
        _xcal(c)
    assert error.value.args == ("This component needs a name for serialization.", c)


def test_component_bool():
    c = Component()
    assert c
