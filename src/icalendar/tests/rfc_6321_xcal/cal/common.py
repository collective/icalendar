from xml.etree.ElementTree import Element, tostring

from icalendar.cal.component import Component


def _xcal(component: Component) -> Element:
    """Return the xCal of a component."""
    e = Element("vcalendar")
    component.to_xcal(e)
    print(tostring(e, method="xml").decode())
    assert len(e) == 1
    return e[0]
