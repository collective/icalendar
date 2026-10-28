"""BINARY XML properties use extension elements in xCal (issue #1982)."""

from io import BytesIO
from xml.etree.ElementTree import ParseError, fromstring

import pytest

from icalendar import Event, InvalidCalendar, config, vBinary, vXml

XML = '<a xmlns="urn:example:binary-xml">café<b/> tail</a>'


@pytest.mark.parametrize("encoding", ["utf-8", "iso-8859-1", "utf-16"])
@pytest.mark.parametrize("source_format", ["object", "ical", "jcal"])
def test_binary_xml_to_xcal(encoding, source_format):
    """Binary XML is decoded by its declaration and written as an extension."""
    data = f'<?xml version="1.0" encoding="{encoding}"?>{XML}'.encode(encoding)
    event = Event()
    event.add("XML", data, parameters={"VALUE": "BINARY"})
    if source_format == "ical":
        event = Event.from_ical(event.to_ical())
    elif source_format == "jcal":
        event = Event.from_jcal(event.to_jcal())
    original_ical, original_jcal = event.to_ical(), event.to_jcal()

    xcal = event.to_xcal(indent=2)
    properties = fromstring(xcal)[0][0]
    assert [child.tag for child in properties] == ["{urn:example:binary-xml}a"]
    copy = Event.from_xcal(xcal)[0]
    assert copy["XML"] == vXml(XML)
    assert copy["XML"].element[0].tail == " tail"
    assert event["XML"].bytes == data
    assert event.to_ical() == original_ical
    assert event.to_jcal() == original_jcal


def test_binary_xml_to_xml():
    """Conversion preserves XML and extra parameters without changing the binary."""
    value = vBinary(XML.encode(), params={"X-PARAM": "value"})
    converted = value.to_xml()
    assert isinstance(converted, vXml)
    assert converted == vXml(XML)
    assert converted.params == {"X-PARAM": "value"}
    converted.params["X-PARAM"] = "changed"
    assert value.params == {
        "ENCODING": "BASE64",
        "VALUE": "BINARY",
        "X-PARAM": "value",
    }
    assert value.bytes == XML.encode()


def test_binary_xml_to_xml_uses_configured_parser(monkeypatch):
    """The configured XML parser receives the unmodified bytes."""
    parse_xml = config.parse_xml
    seen = []

    def parse(source):
        seen.append(source.read())
        return parse_xml(BytesIO(seen[-1]))

    monkeypatch.setattr(config, "parse_xml", parse)
    converted = vBinary(XML.encode()).to_xml()
    assert seen == [XML.encode()]
    assert converted.element.text == "café"


@pytest.mark.parametrize(("encoded", "text"), [(b"\x7f", "\x7f"), (b"&#13;", "\r")])
def test_binary_xml_preserves_characters_not_allowed_in_text(encoded, text):
    """Valid XML characters survive conversion even when TEXT would change them."""
    value = vBinary(b'<a xmlns="urn:x">' + encoded + b"</a>")
    converted = value.to_xml()
    assert converted.element.text == text
    event = Event()
    event.add("XML", converted)
    assert Event.from_ical(event.to_ical())["XML"].element.text == text


@pytest.mark.parametrize("text", [XML, "not XML"])
def test_vxml_to_xml_returns_itself(text):
    """Existing XML values retain their identity, including lazy validation."""
    value = vXml(text)
    assert value.to_xml() is value


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"not XML",
        b"<a>",
        b"<a/><b/>",
        b'<a xmlns="urn:x">\x00</a>',
        b'<a xmlns="urn:x">\x0b</a>',
        b'<a xmlns="urn:x">\xff</a>',
        b'<?xml version="1.0" encoding="no-such-encoding"?><a xmlns="urn:x"/>',
    ],
)
def test_invalid_binary_xml_to_xcal(data):
    """Malformed XML is rejected, not silently repaired as TEXT."""
    value = vBinary(data)
    with pytest.raises(ParseError):
        value.to_xml()
    event = Event()
    event.add("XML", value)
    with pytest.raises(InvalidCalendar, match="Cannot write the XML property"):
        event.to_xcal()
    assert value.bytes == data


@pytest.mark.parametrize(
    "xml",
    ["<a/>", '<a xmlns="urn:ietf:params:xml:ns:icalendar-2.0"/>'],
)
def test_binary_xml_to_xcal_requires_extension_namespace(xml):
    """Binary XML has the same namespace requirements as TEXT XML."""
    event = Event()
    event.add("XML", vBinary(xml))
    with pytest.raises(InvalidCalendar, match="namespace other than"):
        event.to_xcal()


def test_binary_xml_to_xcal_rejects_extra_parameters():
    """Only the binary representation's VALUE and ENCODING are discarded."""
    event = Event()
    event.add("XML", vBinary(XML, params={"X-PARAM": "value"}))
    with pytest.raises(InvalidCalendar, match="X-PARAM"):
        event.to_xcal()


@pytest.mark.parametrize("data", [XML.encode(), bytes(range(256))])
def test_binary_attachment_is_unchanged(data):
    """Ordinary BINARY properties remain Base64 even when their bytes are XML."""
    event = Event()
    event.add("ATTACH", vBinary(data))
    copy = Event.from_xcal(event.to_xcal())[0]
    assert isinstance(copy["ATTACH"], vBinary)
    assert copy["ATTACH"].bytes == data
