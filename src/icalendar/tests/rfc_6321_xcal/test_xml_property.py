"""The XML property.

> The value of this property is a single XML 1.0
> [W3C.REC-xml-20081126] element.
> ...
> The default value type for this property is "TEXT", and normal
> BACKSLASH character encoding rules for that value MUST be applied.
> ...
> If this is the case, then the XML data MUST be
> base64 encoded.  As required by [RFC5545], the "ENCODING" property
> parameter MUST be present and set to "BASE64", and the "VALUE"
> property parameter MUST be present and set to "BINARY".
> - https://datatracker.ietf.org/doc/html/rfc6321#section-4.2

> Extensions that are in a namespace other than the iCalendar XML
> namespace SHOULD be preserved in the iCalendar representation using
> the "XML" iCalendar property described in Section 4.2.
> - https://datatracker.ietf.org/doc/html/rfc6321#section-4.1
"""

import base64
from xml.etree.ElementTree import ParseError, fromstring

import pytest

from icalendar import Calendar, Component, Event, vBroken, vXml

KML = (
    '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    "  <Document>\n"
    "    <name>KML Sample</name>\n"
    "    <open>1</open>\n"
    "    <description>An incomplete example of a KML document - used as an example!</description>\n"
    "  </Document>\n"
    "</kml>"
)
XML = '<a xmlns="http://example.com/ns">text</a>'
XML_BASE64 = base64.b64encode(XML.encode()).decode()
BINARY = {"ENCODING": "BASE64", "VALUE": "BINARY"}


def unfold(ical: bytes) -> bytes:
    """Return the content lines without line folding."""
    return ical.replace(b"\r\n ", b"")


def test_xml_property_is_parsed_as_vxml():
    """The XML property has its own value type."""
    event = Event.from_ical(f"BEGIN:VEVENT\r\nXML:{XML}\r\nEND:VEVENT\r\n")
    assert isinstance(event["XML"], vXml)
    assert event["XML"] == XML
    assert event["XML"].element.text == "text"


def test_text_is_escaped():
    """The XML is written as TEXT with backslash escapes."""
    xml = '<a xmlns="http://example.com/ns">a, b; c\\d\n</a>'
    event = Event()
    event.add("XML", xml)
    ical = event.to_ical()
    line = b'XML:<a xmlns="http://example.com/ns">a\\, b\\; c\\\\d\\n</a>'
    assert line in unfold(ical)
    assert str(Event.from_ical(ical)["XML"]) == xml


def test_rfc_example_round_trip():
    """The KML example of RFC 6321 keeps its content."""
    event = Event()
    event.add("XML", KML)
    xml = Event.from_ical(event.to_ical())["XML"]
    assert str(xml) == KML
    assert xml.element[0][0].text == "KML Sample"


def test_create_from_element():
    """An element is stored as XML without its tail."""
    parent = fromstring('<p xmlns="http://example.com/ns"><a>text</a>tail</p>')
    xml = vXml(parent[0])
    assert xml.element.tag == "{http://example.com/ns}a"
    assert xml.element.text == "text"
    assert "tail" not in xml
    assert parent[0].tail == "tail"


def test_element_is_a_new_element():
    """Changing the element does not change the value."""
    xml = vXml(XML)
    element = xml.element
    element.text = "changed"
    assert xml.element.text == "text"
    assert xml == XML


def test_invalid_xml_has_no_element():
    """Invalid XML can be stored but not parsed."""
    xml = vXml("<a>")
    with pytest.raises(ParseError):
        xml.element


def test_parse_base64():
    """BINARY XML is decoded and written again in Base64."""
    ical = f"BEGIN:VEVENT\r\nXML;ENCODING=BASE64;VALUE=BINARY:{XML_BASE64}\r\nEND:VEVENT\r\n"
    event = Event.from_ical(ical)
    assert isinstance(event["XML"], vXml)
    assert event["XML"] == XML
    assert event["XML"].element.text == "text"
    assert unfold(event.to_ical()) == ical.encode()


def test_write_base64():
    """The ENCODING and VALUE parameters write the XML in Base64."""
    event = Event()
    event.add("XML", XML, parameters=BINARY)
    assert isinstance(event["XML"], vXml)
    line = f"XML;ENCODING=BASE64;VALUE=BINARY:{XML_BASE64}\r\n".encode()
    assert line in unfold(event.to_ical())


def test_invalid_base64_is_broken():
    """Invalid Base64 creates a broken property if errors are ignored."""
    event = Event.from_ical(
        "BEGIN:VEVENT\r\nXML;ENCODING=BASE64;VALUE=BINARY:!!!\r\nEND:VEVENT\r\n"
    )
    assert isinstance(event["XML"], vBroken)


def test_invalid_base64_raises_an_error():
    """Invalid Base64 raises an error if errors are not ignored."""
    with pytest.raises(ValueError, match="base 64"):
        Calendar.from_ical(
            "BEGIN:VCALENDAR\r\nXML;ENCODING=BASE64;VALUE=BINARY:!!!\r\nEND:VCALENDAR\r\n"
        )


@pytest.mark.parametrize(
    ("params", "jcal"),
    [
        ({}, ["xml", {}, "text", XML]),
        (BINARY, ["xml", {}, "binary", XML_BASE64]),
    ],
)
def test_jcal(params, jcal):
    """TEXT and BINARY XML round-trip through jCal."""
    event = Event()
    event.add("XML", vXml(XML, params=params))
    assert event.to_jcal()[1] == [jcal]
    copy = Component.from_jcal(event.to_jcal())
    assert isinstance(copy["XML"], vXml)
    assert copy.to_ical() == event.to_ical()


def test_extension_elements_become_xml_properties(calendars):
    """Elements in other namespaces become XML properties."""
    calendar = calendars.rfc_6321_xml_property_xcal
    event = calendar.events[0]
    assert "KML" not in event
    assert "NOTE" not in event
    assert [xml.element.tag for xml in event.XML] == [
        "{http://www.opengis.net/kml/2.2}kml",
        "{http://example.com/ns/ext}note",
    ]
    assert calendar.XML[0].element.text == "a, b; c\\d"
    assert calendar.XML[0].element.attrib == {"{http://example.com/ns/ext}id": "1"}


@pytest.mark.parametrize("indent", [None, 1, 2, "\t"])
def test_xml_is_embedded_into_xcal(calendars, indent):
    """The XML is part of the properties and keeps its whitespace."""
    calendar = calendars.rfc_6321_xml_property_xcal
    xcal = calendar.to_xcal(indent=indent)
    assert b"<xml>" not in xcal
    copy = Calendar.from_xcal(xcal)[0]
    assert list(map(str, copy.XML)) == list(map(str, calendar.XML))
    assert list(map(str, copy.events[0].XML)) == list(map(str, calendar.events[0].XML))


def test_ical_to_xcal_and_back():
    """The XML keeps its meaning when converted to xCal and back."""
    event = Event()
    event.XML = [KML, '<b:x xmlns:b="http://example.com/b" b:a="1"/>']
    copy = Event.from_xcal(event.to_xcal(indent=2))[0]
    assert copy.XML == event.XML
    assert copy == event


@pytest.mark.parametrize("indent", [None, 2])
@pytest.mark.parametrize(
    "xml",
    [
        '<x:a xmlns:x="http://example.com/x"><b>no namespace</b></x:a>',
        '<x:a xmlns:x="http://example.com/x"><properties><x:b>t</x:b>\n</properties></x:a>',
    ],
)
def test_elements_without_namespace_stay_without_namespace(xml, indent):
    """Elements without a namespace do not get the iCalendar namespace in xCal."""
    event = Event()
    event.add("XML", xml)
    copy = Event.from_xcal(event.to_xcal(indent=indent))[0]
    assert copy["XML"] == event["XML"]


@pytest.mark.parametrize(
    ("xml", "params"),
    [
        ("<a>no namespace</a>", {}),
        ('<a xmlns="urn:ietf:params:xml:ns:icalendar-2.0"/>', {}),
        (XML, {"X-PARAM": "value"}),
        ("not XML", {}),
    ],
)
def test_xml_that_cannot_be_embedded(xml, params):
    """XML that cannot be embedded is written as an xml property."""
    event = Event()
    event.add("XML", vXml(xml, params=params))
    xcal = event.to_xcal(indent=2)
    assert b"<xml>" in xcal
    copy = Event.from_xcal(xcal)[0]
    assert str(copy["XML"]) == xml
    assert dict(copy["XML"].params) == params


def test_xml_in_any_component(component):
    """The XML property can be specified multiple times in any component."""
    assert component.XML == []
    component.XML = [XML, fromstring('<b xmlns="http://example.com/b"/>')]
    assert [xml.element.tag for xml in component.XML] == [
        "{http://example.com/ns}a",
        "{http://example.com/b}b",
    ]
    assert unfold(component.to_ical()).count(b"\r\nXML:") == 2
    del component.XML
    assert component.XML == []
    assert "XML" not in component


@pytest.mark.parametrize("empty", [None, []])
def test_remove_xml(empty):
    """Assigning nothing removes the XML properties."""
    event = Event()
    event.XML = XML
    event.XML = empty
    assert "XML" not in event


def test_equality_ignores_namespace_prefixes():
    """Values are equal if their XML is equal."""
    xml = vXml('<a xmlns="http://example.com/ns"><b>t</b></a>')
    same = vXml('<n:a xmlns:n="http://example.com/ns"><n:b>t</n:b></n:a>')
    other = vXml('<a xmlns="http://example.com/ns"><b>u</b></a>')
    assert xml == same
    assert (xml != same) is False
    assert hash(xml) == hash(same)
    assert xml != other
    assert (xml == other) is False


def test_invalid_xml_is_compared_as_text():
    """Values that are not XML are equal if their text is equal."""
    assert vXml("<a>") == vXml("<a>")
    assert vXml("<a>") != vXml("<b>")
    assert hash(vXml("<a>")) == hash(vXml("<a>"))
