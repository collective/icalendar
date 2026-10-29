"""The XML property.

The tests follow the plan in
https://github.com/collective/icalendar/pull/1958#discussion_r4324499271

> The value of this property is a single XML 1.0
> [W3C.REC-xml-20081126] element.
> ...
> The default value type for this property is "TEXT", and normal
> BACKSLASH character encoding rules for that value MUST be applied.
> - https://datatracker.ietf.org/doc/html/rfc6321#section-4.2

> Extensions that are in a namespace other than the iCalendar XML
> namespace SHOULD be preserved in the iCalendar representation using
> the "XML" iCalendar property described in Section 4.2.  Only those
> extension elements that are immediate child elements of the IC:
> properties element are converted, any others are ignored.
> - https://datatracker.ietf.org/doc/html/rfc6321#section-4.1
"""

import base64
import re
import xml.etree.ElementTree as ET
from io import BytesIO
from xml.etree.ElementTree import Element, ParseError, fromstring, tostring

import pytest

from icalendar import (
    Calendar,
    Component,
    Event,
    InvalidCalendar,
    TypesFactory,
    config,
    vBinary,
    vText,
    vUnknown,
    vXml,
)
from icalendar.parser.xcal.adapter import ElementAdapter
from icalendar.parser.xcal.property import XCalPropertyParser

XML = '<a xmlns="http://example.com/ns">text</a>'
XML_BASE64 = base64.b64encode(XML.encode()).decode()
KML = (
    '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    "  <Document>\n"
    "    <name>KML Sample</name>\n"
    "    <open>1</open>\n"
    "    <description>An incomplete example of a KML document - used as an example!</description>\n"
    "  </Document>\n"
    "</kml>"
)


def unfold(ical: bytes) -> bytes:
    """Return the content lines without line folding."""
    return ical.replace(b"\r\n ", b"")


def xcal_event(properties: str) -> bytes:
    """Return xCal with an event that has these properties."""
    return (
        '<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">'
        f"<vevent><properties>{properties}</properties></vevent>"
        "</icalendar>"
    ).encode()


def normalized(xml) -> str:
    """Return the XML with the namespace prefixes of ElementTree."""
    return tostring(vXml(xml).element, encoding="unicode")


def xml_parts(xcal: bytes) -> list[list[str]]:
    """Return the XML properties for each properties element in xCal."""
    return [
        [
            normalized(element)
            for element in e_properties
            if ElementAdapter(element).is_extension
        ]
        for e_properties in fromstring(xcal).iter(
            "{urn:ietf:params:xml:ns:icalendar-2.0}properties"
        )
    ]


# xCal -> icalendar objects


@pytest.mark.parametrize(
    ("tag", "is_extension"),
    [
        ("properties", False),
        ("{urn:ietf:params:xml:ns:icalendar-2.0}properties", False),
        ("{http://www.opengis.net/kml/2.2}kml", True),
        ("{urn:ietf:params:xml:ns:icalendar-2.0/ext}kml", True),
    ],
)
def test_xml_property_from_xcal_other_namespaces(tag, is_extension):
    """Only elements in other namespaces than iCalendar are XML properties."""
    assert ElementAdapter(Element(tag)).is_extension is is_extension


def test_xml_property_from_xcal_example_file(calendars):
    """The elements in other namespaces in the properties are XML properties."""
    calendar = calendars.rfc_6321_xml_property_xcal
    event = calendar.events[0]
    assert "KML" not in event
    assert "NOTE" not in event
    assert all(isinstance(xml, vXml) for xml in calendar.XML + event.XML)
    assert [xml.element.tag for xml in event.XML] == [
        "{http://www.opengis.net/kml/2.2}kml",
        "{http://example.com/ns/ext}note",
    ]
    assert calendar.XML[0].element.text == "a, b; c\\d"
    assert calendar.XML[0].element.attrib == {"{http://example.com/ns/ext}id": "1"}


def test_xml_property_from_xcal_keeps_the_element():
    """The value keeps the element with its path in the xCal, without parsing."""
    xml = Event.from_xcal(xcal_event(XML))[0]["XML"]
    assert xml._element.get_xpath() == "/icalendar/vevent[1]/properties[1]/a[1]"
    assert xml.element.text == "text"
    assert xml.element.tail is None


def test_xml_property_from_xcal_without_the_icalendar_namespace():
    """xCal without the iCalendar namespace still has XML properties."""
    xcal = (
        "<icalendar><vevent><properties>"
        "<summary><text>Meeting</text></summary>"
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document/></kml>'
        "</properties></vevent></icalendar>"
    )
    event = Event.from_xcal(xcal.encode())[0]
    assert event["SUMMARY"] == "Meeting"
    assert event["XML"].element.tag == "{http://www.opengis.net/kml/2.2}kml"


@pytest.mark.parametrize(
    "xcal",
    [
        pytest.param(lambda: fromstring(XML), id="Element"),
        pytest.param(lambda: ElementAdapter(fromstring(XML)), id="ElementAdapter"),
        pytest.param(lambda: XCalPropertyParser(fromstring(XML)), id="parser"),
    ],
)
def test_xml_property_from_xcal_of_the_element(xcal):
    """The XML element is the value, also when a parser is given."""
    assert vXml.from_xcal(xcal()).element.text == "text"


def test_xml_property_from_xcal_of_an_xml_property_element():
    """An xml property element is parsed like other TEXT properties."""
    element = fromstring("<xml><text>&lt;a xmlns=&quot;urn:x&quot;/&gt;</text></xml>")
    assert str(vXml.from_xcal(XCalPropertyParser(element))) == '<a xmlns="urn:x"/>'
    assert str(vXml.from_xcal(element)) == '<a xmlns="urn:x"/>'


def test_xml_property_from_xcal_reads_what_to_xcal_writes():
    """The value can be parsed from the element that it writes."""
    element = Element("xml")
    vXml(XML).to_xcal(element)
    assert element.tag == "{http://example.com/ns}a"
    assert vXml.from_xcal(element) == vXml(XML)


@pytest.mark.parametrize(
    "properties",
    [
        # case C: an element in another namespace inside of a property
        (
            "<new-property><parameters/>"
            '<custom xmlns="http://example.com/ns">Hello</custom></new-property>'
        ),
        # case D: an element in another namespace inside of an unknown value type
        (
            "<new-property><parameters/>"
            '<custom><root xmlns="http://example.com/ns">Hello</root></custom>'
            "</new-property>"
        ),
    ],
)
def test_xml_property_from_xcal_only_directly_in_properties(properties):
    """Elements in other namespaces inside of a property are not XML properties."""
    event = Event.from_xcal(xcal_event(properties))[0]
    assert "XML" not in event


# icalendar objects -> xCal


@pytest.mark.parametrize("params", [{}, {"VALUE": "TEXT"}])
def test_xml_property_to_xcal_replaces_the_property(params):
    """The XML element takes the place of the xml element."""
    event = Event()
    event.add("XML", vXml(XML, params=params))
    e_properties = fromstring(event.to_xcal())[0][0]
    assert [element.tag for element in e_properties] == ["{http://example.com/ns}a"]
    assert e_properties[0].text == "text"


@pytest.mark.parametrize("indent", [None, 1, 2, "\t"])
def test_xml_property_to_xcal_keeps_the_whitespace(indent):
    """Indenting the xCal does not change the XML."""
    event = Event()
    event.XML = [KML, XML]
    copy = Event.from_xcal(event.to_xcal(indent=indent))[0]
    assert list(map(normalized, copy.XML)) == list(map(normalized, event.XML))


@pytest.mark.parametrize("indent", [None, "\t"])
def test_xml_property_to_xcal_example_file(calendars, indent):
    """The XML parts of the example file are in the same place after a round trip.

    See https://github.com/collective/icalendar/pull/1958#discussion_r4324585541
    """
    calendar = calendars.rfc_6321_xml_property_xcal
    expected = xml_parts(calendar.raw_xcal)
    assert list(map(len, expected)) == [1, 2]
    assert xml_parts(calendar.to_xcal(indent=indent)) == expected


@pytest.mark.parametrize("indent", [None, 2])
@pytest.mark.parametrize(
    "xml",
    [
        '<x:a xmlns:x="http://example.com/x"><b>no namespace</b></x:a>',
        '<x:a xmlns:x="http://example.com/x"><properties><x:b>t</x:b>\n</properties></x:a>',
    ],
)
def test_xml_property_to_xcal_elements_without_namespace(xml, indent):
    """Elements without a namespace do not get the iCalendar namespace."""
    event = Event()
    event.add("XML", xml)
    copy = Event.from_xcal(event.to_xcal(indent=indent))[0]
    assert normalized(copy["XML"]) == normalized(xml)


@pytest.mark.parametrize(
    ("xml", "expected"),
    [
        ('<n:a xmlns:n="urn:x" n:b="1"/>', '<ns0:a xmlns:ns0="urn:x" ns0:b="1" />'),
        ('<?xml version="1.0"?><a xmlns="urn:x"/>', '<ns0:a xmlns:ns0="urn:x" />'),
        ('<!DOCTYPE a><a xmlns="urn:x"/>', '<ns0:a xmlns:ns0="urn:x" />'),
        ('<a xmlns="urn:x"><!-- comment --></a>', '<ns0:a xmlns:ns0="urn:x" />'),
        (
            '<a xmlns="urn:x"><![CDATA[<b>]]></a>',
            '<ns0:a xmlns:ns0="urn:x">&lt;b&gt;</ns0:a>',
        ),
    ],
)
def test_xml_property_to_xcal_and_back(xml, expected):
    """ElementTree writes the XML element.

    It chooses the namespace prefixes and leaves out
    the XML declaration, the document type and comments.
    """
    event = Event()
    event.add("XML", xml)
    assert str(Event.from_xcal(event.to_xcal())[0]["XML"]) == expected


def test_xml_property_to_xcal_and_back_is_equal():
    """The event is equal after a round trip, although the prefixes change."""
    event = Event()
    event.XML = [KML, '<b:x xmlns:b="http://example.com/b" b:a="1"/>']
    copy = Event.from_xcal(event.to_xcal(indent=2))[0]
    assert copy == event
    assert str(copy.XML[1]) == '<ns0:x xmlns:ns0="http://example.com/b" ns0:a="1" />'


@pytest.mark.parametrize(
    "declaration",
    [
        '<?xml version="1.0" encoding="ISO-8859-1"?>',
        '<?xml version="1.0" encoding="windows-1252"?>',
        '<?xml version="1.0" encoding="US-ASCII"?>',
        "<?xml version='1.0' encoding='UTF-16' standalone='yes'?>",
        chr(0xFEFF) + '<?xml version="1.0" encoding="ISO-8859-1"?>',
    ],
)
def test_xml_property_to_xcal_ignores_the_declared_encoding(declaration):
    """The text is already decoded, so the encoding of its declaration is ignored."""
    event = Event()
    event.add("XML", f'{declaration}<a xmlns="urn:x">café €</a>')
    assert event["XML"].element.text == "café €"
    assert Event.from_xcal(event.to_xcal())[0]["XML"].element.text == "café €"


# icalendar objects -> iCal/jCal


def test_xml_property_to_ical_escapes_the_text():
    """The XML is written as TEXT with backslash escapes."""
    event = Event()
    event.add("XML", '<a xmlns="http://example.com/ns">a, b; c\\d\n</a>')
    line = b'XML:<a xmlns="http://example.com/ns">a\\, b\\; c\\\\d\\n</a>'
    assert line in unfold(event.to_ical())


def test_xml_property_to_jcal_is_text():
    """The XML is a text value in jCal."""
    event = Event()
    event.add("XML", XML)
    assert event.to_jcal()[1] == [["xml", {}, "text", XML]]


def test_xml_property_to_ical_binary():
    """XML with the value type BINARY is written in Base64."""
    event = Event()
    event.add("XML", XML, parameters={"VALUE": "BINARY"})
    assert isinstance(event["XML"], vBinary)
    line = f"\r\nXML;ENCODING=BASE64;VALUE=BINARY:{XML_BASE64}\r\n".encode()
    assert line in unfold(event.to_ical())


def test_xml_property_to_jcal_binary():
    """XML with the value type BINARY is a binary value in jCal."""
    event = Event()
    event.add("XML", XML, parameters={"VALUE": "BINARY"})
    assert event.to_jcal()[1] == [["xml", {}, "binary", XML_BASE64]]


# iCal/jCal -> icalendar objects


@pytest.mark.parametrize(
    ("name", "value", "value_type"),
    [
        ("XML", None, vXml),
        ("XML", "TEXT", vXml),
        ("XML", "BINARY", vBinary),
        ("X-FOO", "XML", vUnknown),
    ],
)
def test_xml_property_from_ical_value_type(name, value, value_type):
    """XML is a property with the value types TEXT and BINARY, not a value type."""
    assert TypesFactory.instance().for_property(name, value) is value_type


def test_xml_property_from_ical_is_vxml():
    """The XML property is a vXml."""
    event = Event.from_ical(f"BEGIN:VEVENT\r\nXML:{XML}\r\nEND:VEVENT\r\n")
    assert isinstance(event["XML"], vXml)
    assert event["XML"] == vXml(XML)
    assert event["XML"].ical_value.tag == "{http://example.com/ns}a"
    assert event["XML"].element.text == "text"


def test_xml_property_from_ical_rfc_example(calendars):
    """The KML example of RFC 6321 keeps its content."""
    xml = calendars.rfc_6321_xml_property_ical.events[0]["XML"]
    assert isinstance(xml, vXml)
    assert str(xml) == KML
    assert xml.element[0][0].text == "KML Sample"


def test_xml_property_from_ical_binary():
    """XML with the value type BINARY is a vBinary."""
    ical = (
        "BEGIN:VEVENT\r\n"
        f"XML;ENCODING=BASE64;VALUE=BINARY:{XML_BASE64}\r\n"
        "END:VEVENT\r\n"
    )
    event = Event.from_ical(ical)
    assert isinstance(event["XML"], vBinary)
    assert event["XML"].bytes == XML.encode()
    assert unfold(event.to_ical()) == ical.encode()


ANY_TEXT = [
    XML,
    "<a>no namespace</a>",
    '<a xmlns="urn:ietf:params:xml:ns:icalendar-2.0"/>',
    "not XML",
    "PGEvPg==",
    "<a/><b/>",
    '<?xml version="1.0"?><a xmlns="urn:x"/>',
    '<a xmlns="urn:x"><![CDATA[<b>]]></a>',
]


@pytest.mark.parametrize("text", ANY_TEXT)
def test_xml_property_from_ical_any_text(text):
    """Any text is a vXml and is written as it is."""
    ical = f"BEGIN:VCALENDAR\r\nXML:{text}\r\nEND:VCALENDAR\r\n"
    calendar = Calendar.from_ical(ical)
    assert isinstance(calendar["XML"], vXml)
    assert calendar["XML"] == text
    assert calendar.to_ical() == ical.encode()


@pytest.mark.parametrize("text", ANY_TEXT)
def test_xml_property_from_jcal_any_text(text):
    """Any text is a vXml and is written as it is."""
    jcal = ["vcalendar", [["xml", {}, "text", text]], []]
    calendar = Calendar.from_jcal(jcal)
    assert isinstance(calendar["XML"], vXml)
    assert calendar.to_jcal() == jcal


def test_xml_property_from_jcal_binary():
    """XML with the value type BINARY is a vBinary."""
    jcal = ["vevent", [["xml", {}, "binary", XML_BASE64]], []]
    event = Event.from_jcal(jcal)
    assert isinstance(event["XML"], vBinary)
    assert event.to_jcal() == jcal


# setting XML -> xCal/jCal/iCal

XML_VALUES = {
    "str": lambda: XML,
    "bytes": XML.encode,
    "vXml": lambda: vXml(XML),
    "Element": lambda: fromstring(XML),
    "ElementAdapter": lambda: ElementAdapter(fromstring(XML)),
}


def set_xml(event: Event, setter: str, xml) -> None:
    """Set the XML property of the event."""
    if setter == "add":
        event.add("XML", xml)
    elif setter == "XML":
        event.XML = xml
    else:
        event["XML"] = xml


@pytest.fixture(
    params=[
        *(("add", value) for value in XML_VALUES),
        *(("XML", value) for value in XML_VALUES),
        # For other values, see https://github.com/collective/icalendar/issues/1983
        ("[]", "vXml"),
    ],
    ids="-".join,
)
def event_with_xml(request) -> Event:
    """An event with XML that is set in different ways."""
    setter, value = request.param
    event = Event()
    set_xml(event, setter, XML_VALUES[value]())
    return event


def test_xml_to_ical(event_with_xml):
    """The XML stays the same in iCal."""
    copy = Event.from_ical(event_with_xml.to_ical())
    assert isinstance(copy["XML"], vXml)
    assert normalized(copy["XML"]) == normalized(XML)


def test_xml_to_jcal(event_with_xml):
    """The XML stays the same in jCal."""
    copy = Component.from_jcal(event_with_xml.to_jcal())
    assert isinstance(copy["XML"], vXml)
    assert normalized(copy["XML"]) == normalized(XML)


def test_xml_to_xcal(event_with_xml):
    """The XML element takes the place of the property in xCal."""
    xcal = event_with_xml.to_xcal()
    assert [element.tag for element in fromstring(xcal)[0][0]] == [
        "{http://example.com/ns}a"
    ]
    copy = Event.from_xcal(xcal)[0]
    assert isinstance(copy["XML"], vXml)
    assert normalized(copy["XML"]) == normalized(XML)


@pytest.mark.parametrize("setter", ["add", "XML", "[]"])
def test_xml_to_xcal_vtext(setter):
    """A vText is not converted, so it is written as text in xCal."""
    event = Event()
    set_xml(event, setter, vText(XML))
    assert type(event["XML"]) is vText
    xcal = event.to_xcal()
    assert [element.tag for element in fromstring(xcal)[0][0]] == [
        "{urn:ietf:params:xml:ns:icalendar-2.0}xml"
    ]
    copy = Event.from_xcal(xcal)[0]
    assert isinstance(copy["XML"], vXml)
    assert copy["XML"] == XML


def test_xml_to_xcal_element_with_control_characters():
    """Control characters are removed from the element, too."""
    element = Element("{http://example.com/ns}a")
    element.text = "a\x0bb"
    event = Event()
    event.add("XML", element)
    assert event["XML"].element.text == "ab"
    assert Event.from_xcal(event.to_xcal())[0]["XML"].element.text == "ab"


@pytest.mark.parametrize(
    "data",
    [
        '<?xml version="1.0" encoding="ISO-8859-1"?><a xmlns="urn:x">café</a>'.encode(
            "ISO-8859-1"
        ),
        '<a xmlns="urn:x">café</a>'.encode(),
    ],
)
def test_xml_to_xcal_bytes(data):
    """Bytes are decoded with the encoding of their XML declaration."""
    event = Event()
    event.add("XML", data)
    assert event["XML"].element.text == "café"
    assert Event.from_xcal(event.to_xcal())[0]["XML"].element.text == "café"


def test_xml_to_ical_without_the_tail_of_the_element():
    """The tail of an element is not part of the XML."""
    parent = fromstring('<p xmlns="http://example.com/ns"><a>text</a>tail</p>')
    event = Event()
    event.add("XML", parent[0])
    assert b"tail" not in event.to_ical()
    assert event["XML"].element.tail is None
    assert parent[0].tail == "tail"


# vXml


@pytest.mark.parametrize("from_element", [True, False])
def test_vxml_element_is_a_copy(from_element):
    """Changing an element does not change the value."""
    element = fromstring(XML)
    value = vXml(element if from_element else XML)
    element.text = "changed"
    value.element.text = "changed"
    assert value.element.text == "text"


def test_vxml_element_of_text_that_is_not_xml():
    """Text that is not XML has no element."""
    with pytest.raises(ParseError):
        vXml("<a>").element


def test_vxml_equality_ignores_namespace_prefixes():
    """Values are equal if their XML is equal."""
    xml = vXml('<a xmlns="http://example.com/ns"><b>t</b></a>')
    same = vXml('<n:a xmlns:n="http://example.com/ns"><n:b>t</n:b></n:a>')
    other = vXml('<a xmlns="http://example.com/ns"><b>u</b></a>')
    assert xml == same
    assert (xml != same) is False
    assert hash(xml) == hash(same)
    assert xml != other
    assert (xml == other) is False


def test_vxml_equality_ignores_the_order_of_attributes():
    """The order of the attributes does not matter."""
    xml = vXml('<a xmlns="urn:x" p="1" q="2"/>')
    same = vXml('<a xmlns="urn:x" q="2" p="1"/>')
    assert xml == same
    assert hash(xml) == hash(same)


@pytest.mark.parametrize(
    ("xml", "other"),
    [
        ('<a xmlns="urn:x"><b/>x</a>', '<a xmlns="urn:x"><b/>y</a>'),
        ('<a xmlns="urn:x"><b/><c/></a>', '<a xmlns="urn:x"><b><c/></b></a>'),
    ],
)
def test_vxml_equality_compares_the_tails_and_the_tree(xml, other):
    """The tails and the places of the elements are compared, too."""
    assert vXml(xml) != vXml(other)
    assert (vXml(xml) == vXml(other)) is False


def test_vxml_is_not_equal_to_other_types():
    """A value is not equal to an object that is not a string."""
    assert vXml(XML) != 1
    assert vXml(XML) != object()
    assert (vXml(XML) == 1) is False
    assert 1 != vXml(XML)
    assert object() != vXml(XML)
    assert (1 == vXml(XML)) is False


def test_vxml_equality_of_text_that_is_not_xml():
    """Values that are not XML are equal if their text is equal."""
    assert vXml("<a>") == vXml("<a>")
    assert vXml("<a>") != vXml("<b>")
    assert hash(vXml("<a>")) == hash(vXml("<a>"))


@pytest.mark.parametrize(
    "text",
    [
        pytest.param(
            '<a xmlns="urn:x">' + "<b>" * 1500 + "</b>" * 1500 + "</a>",
            id="deep XML",
        ),
        pytest.param('<a xmlns="urn:x">' + chr(0xD800) + "</a>", id="lone surrogate"),
        pytest.param(
            '<?xml version="1.0" encoding="UTF-8" encoding="no-such-encoding"?>'
            '<a xmlns="urn:x"/>',
            id="unknown encoding",
        ),
    ],
)
def test_vxml_equality_does_not_raise(text):
    """Deep XML and text that is not XML can be compared and hashed."""
    xml = vXml(text)
    assert xml == vXml(text)
    assert xml != vXml(text.replace("urn:x", "urn:y"))
    assert hash(xml) == hash(vXml(text))


def test_vxml_equality_of_xml_with_a_document_type():
    """XML with a document type is compared as text, so it is not expanded."""
    xml = vXml('<!DOCTYPE a [<!ENTITY e "x">]><a xmlns="urn:x">&e;</a>')
    assert xml != vXml('<a xmlns="urn:x">x</a>')
    assert xml == vXml(str(xml))
    assert hash(xml) == hash(str(xml))


def test_vxml_equality_with_an_xml_parser_that_refuses(monkeypatch):
    """If the XML parser refuses the XML, the text is compared."""

    def refuse(_source):
        raise ValueError("refused")

    monkeypatch.setattr(config, "parse_xml", refuse)
    assert vXml(XML) != vXml(XML.replace("text", "other"))
    assert hash(vXml(XML)) == hash(vXml(XML))
    assert (
        vXml(fromstring(XML)) == '<ns0:a xmlns:ns0="http://example.com/ns">text</ns0:a>'
    )


def test_vxml_hash_does_not_depend_on_registered_prefixes(monkeypatch):
    """Registering a namespace prefix in ElementTree does not change the hash."""
    before = hash(vXml('<a xmlns="urn:example:registry"/>'))
    monkeypatch.setitem(ET._namespace_map, "urn:example:registry", "reg")
    assert hash(vXml('<a xmlns="urn:example:registry"/>')) == before


def test_vxml_gives_the_xml_parser_bytes(monkeypatch):
    """vXml uses the configured XML parser with bytes, like Component.from_xcal."""
    parse_xml = config.parse_xml
    data = []

    def read(source):
        data.append(source.read())
        return parse_xml(BytesIO(data[-1]))

    monkeypatch.setattr(config, "parse_xml", read)
    assert vXml(XML).element.text == "text"
    assert data == [XML.encode()]


# Strictness


@pytest.mark.parametrize(
    "text",
    [
        "not XML",
        "",
        "<a/><b/>",
        "<a>no namespace</a>",
        '<a xmlns="urn:ietf:params:xml:ns:icalendar-2.0"/>',
        '<?xml encoding="UTF-8"?><a xmlns="urn:x"/>',
        '<?xml version="1.0"\xa0encoding="UTF-8"?><a xmlns="urn:x"/>',
        '<a xmlns="urn:x">' + chr(0xD800) + "</a>",
    ],
)
def test_to_xcal_broken_xml(text):
    """XML that cannot be written to xCal raises an error."""
    event = Event()
    event.add("XML", text)
    with pytest.raises(InvalidCalendar, match="Cannot write the XML property"):
        event.to_xcal()


def test_to_xcal_broken_xml_in_another_property():
    """vXml can only be written to xCal as the value of the XML property."""
    event = Event()
    event.add("DESCRIPTION", vXml(XML))
    with pytest.raises(InvalidCalendar, match="value of the XML property"):
        event.to_xcal()


def test_to_xcal_broken_xml_tells_how_to_add_a_namespace():
    """The error says how to add a namespace."""
    event = Event()
    event.add("XML", "<a>no namespace</a>")
    with pytest.raises(InvalidCalendar, match=re.escape('<a xmlns="http://')):
        event.to_xcal()


def test_to_xcal_broken_xml_with_parameters():
    """The element of an XML property has no place for parameters in xCal."""
    event = Event()
    event.add("XML", XML, parameters={"X-PARAM": "value"})
    with pytest.raises(InvalidCalendar, match="X-PARAM"):
        event.to_xcal()


def test_from_xcal_broken_xml():
    """An xml element in the iCalendar namespace is parsed like other properties."""
    event = Event.from_xcal(xcal_event("<xml><text>not XML</text></xml>"))[0]
    assert isinstance(event["XML"], vXml)
    assert event["XML"] == "not XML"
    with pytest.raises(InvalidCalendar, match="Cannot write the XML property"):
        event.to_xcal()


# Component.XML


def test_xml_property_in_any_component(component):
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
def test_xml_property_is_removed(empty):
    """Assigning nothing removes the XML properties."""
    event = Event()
    event.XML = XML
    event.XML = empty
    assert "XML" not in event


def test_vxml_bytes_property():
    """vXml exposes a bytes property returning the UTF-8 bytes representation."""
    raw_xml = '<test xmlns="http://example.com/ns">content with unicode: \u20ac</test>'
    v = vXml(raw_xml)
    assert isinstance(v.bytes, bytes)
    assert v.bytes == raw_xml.encode("utf-8")


def test_vxml_and_vbinary_bytes_interface_consistency():
    """vXml and vBinary both provide a .bytes property holding raw binary data."""
    raw_bytes = b'<custom xmlns="http://example.org">binary payload</custom>'
    v_bin = vBinary(raw_bytes)
    v_xml = vXml(raw_bytes.decode("utf-8"))

    assert isinstance(v_bin.bytes, bytes)
    assert isinstance(v_xml.bytes, bytes)
    assert v_bin.bytes == v_xml.bytes == raw_bytes
