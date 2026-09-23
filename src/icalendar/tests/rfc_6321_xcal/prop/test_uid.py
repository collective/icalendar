"""xCal conversion for UID values."""

from xml.etree import ElementTree as ET

from icalendar import vUid

UID = "d755cef5-2311-46ed-a0e1-6733c9e15c63"


def test_to_xcal():
    """Convert UID to xCal."""
    uid = vUid(UID)

    element = uid.to_xcal()

    assert isinstance(element, ET.Element)
    assert element.tag == "text"
    assert element.text == UID


def test_from_xcal():
    """Parse UID from xCal."""
    element = ET.Element("text")
    element.text = UID

    result = vUid.from_xcal(element)

    assert isinstance(result, vUid)
    assert result.ical_value == UID
