"""Text is escaped in XML. This makes sure it round-trips.


These are allowed characters in XML:

https://www.w3.org/TR/REC-xml/#charsets
#x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
/* any Unicode character, excluding the surrogate blocks, FFFE, and FFFF. */

"""

from io import BytesIO
from xml.etree.ElementTree import Element, ElementTree, ParseError

import pytest

from icalendar.config import parse_xml
from icalendar.prop.text import vText
from icalendar.prop.uid import vUid
from icalendar.prop.unknown import vUnknown
from icalendar.prop.uri import vUri
from icalendar.prop.xml_reference import vXmlReference
from icalendar.tests.rfc_6321_xcal.common import to_xcal


def round_trip(xml: Element) -> Element:
    file = BytesIO()
    ElementTree(xml).write(file, "utf-8", xml_declaration=False, method="xml")

    b = file.getvalue()
    try:
        return parse_xml(BytesIO(b)).getroot()
    except ParseError:
        print(b)
        raise


# #x9 | #xA | #xD | [#x20-#xD7FF]
VALID_CHARACTERS_BELOW_SPACE = "\x09\x0a\x0d"
INVALID_CHARACTERS = "".join(
    chr(i) for i in range(0x20) if chr(i) not in VALID_CHARACTERS_BELOW_SPACE
)

VALID_CHARACTERS = "".join(
    chr(i) for i in range(256) if chr(i) not in INVALID_CHARACTERS
)


@pytest.fixture(params=[vText, vUnknown, vUid, vUri, vXmlReference])
def xcal_text_type(request):
    return request.param


@pytest.fixture(
    params=[
        VALID_CHARACTERS,
        " x ",
        "\rx\r",
        "\r\nx\r\n",
        "\nx\n",
        "\tx\t",
        "<a> </a>",
    ],
    ids=["valid", "spaces", "cr", "crlf", "lf", "tab", "tag"],
)
def text(request):
    """The text to round-trip."""
    return request.param


@pytest.mark.parametrize("through_bytes", [True, False])
def test_text_round_trips(text, xcal_text_type, through_bytes):
    """We just check round-tripping.

    vText and subclasses can do newline normalization.
    So, we do not check if the text stays the same.
    """
    try:
        value = xcal_text_type(text)
    except ValueError:
        pytest.skip(f"{xcal_text_type.__name__}({text!r}) cannot be used.")
        return
    xml = to_xcal(value, wrap=True)
    if through_bytes:
        xml = round_trip(xml)
    xml_value = xcal_text_type.from_xcal(xml)
    assert newline_escape(value.ical_value) == newline_escape(xml_value.ical_value)


def newline_escape(text: str) -> str:
    """Mimic XML replacement"""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def test_xml_round_trips(text):
    r"""Check that XML does not change the text.

    This is for learning and asserting how Python escapes text.
    \\r\\n -> \\n
    \\r -> \\n
    """
    element = Element("text")
    element.text = text
    round_tripped = round_trip(element)
    assert round_tripped.text == newline_escape(text)


@pytest.mark.parametrize("text", INVALID_CHARACTERS)
@pytest.mark.parametrize("wrap", ["", "asdasdasdasd"])
def test_invalid_xml_characters_are_replaced(xcal_text_type, text, wrap):
    value = xcal_text_type(wrap + text + wrap)
    element = round_trip(to_xcal(value, wrap=True))
    xvalue = xcal_text_type.from_xcal(element)
    assert xvalue.ical_value == wrap + wrap
