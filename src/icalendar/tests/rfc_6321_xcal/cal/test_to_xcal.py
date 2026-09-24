"""Test component to xcal serialization."""

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.cal.calendar import Calendar
from icalendar.cal.component import Component
from icalendar.cal.event import Event
from icalendar.cal.todo import Todo
from icalendar.tests.rfc_6321_xcal.common import to_xcal


def test_component_to_xcal_uses_component_name(component):
    """The name is lowercase, same as rfc 5545"""
    e = to_xcal(component)
    assert e.tag == component.name.lower()


def test_empty_component(component):
    """Empty component without children."""
    e = to_xcal(component)
    assert len(e) == 0


def test_adding_a_property(component):
    """Test that adding a property turns up."""
    component.add("comment", "this is a comment")
    e = to_xcal(component)
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
        to_xcal(c)
    assert error.value.args == ("This component needs a name for serialization.", c)


def test_component_bool():
    c = Component()
    assert c


def test_serialize_subcomponents():
    """Test serialization of subcomponents."""
    c = Calendar()
    c.add_component(Event())
    c.add_component(Todo())
    c.events[0].add_component(Alarm())
    serialized = to_xcal(c)
    # calendar
    assert serialized.tag == "vcalendar"
    assert len(serialized) == 1
    c_c = serialized[0]
    assert len(c_c) == 2
    assert c_c.tag == "components"
    # event
    c_e = c_c[0]
    assert c_e.tag == "vevent"
    assert len(c_e) == 1
    c_e_c = c_e[0]
    assert c_e_c.tag == "components"
    # alarm
    c_a = c_e_c[0]
    assert c_a.tag == "valarm"
    assert len(c_a) == 0
    # todo
    c_t = c_c[1]
    assert c_t.tag == "vtodo"
    assert len(c_t) == 0


def test_subcomponent_also_serializes_parameters():
    """The subcomponents must also add parameters."""
    e = Event()
    e.summary = "an event"
    a = Alarm()
    a.ACTION = "DISPLAY"
    e.add_component(a)
    x_e = to_xcal(e)
    assert len(x_e) == 2
    assert x_e.tag == "vevent"
    assert x_e[0].tag == "properties"
    assert x_e[0][0].tag == "summary"
    assert x_e[0][0][0].tag == "text"
    assert x_e[0][0][0].text == "an event"
    assert x_e[1].tag == "components"
    assert len(x_e[1]) == 1
    assert x_e[1][0].tag == "valarm"
    assert len(x_e[1][0]) == 1
    assert x_e[1][0][0].tag == "properties"
    assert len(x_e[1][0][0]) == 1
    assert x_e[1][0][0][0].tag == "action"
    assert len(x_e[1][0][0][0]) == 1
    assert x_e[1][0][0][0][0].tag == "text"
    assert x_e[1][0][0][0][0].text == "DISPLAY"
