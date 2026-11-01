"""float converison

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.2
https://datypic.com/sc/xsd/t-xsd_float.html
"""

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.integer import vInt
from icalendar.tests.rfc_6321_xcal.common import (
    XML_WHITESPACE,
    list2xml,
    to_xcal,
    xml2list,
)


@pytest.mark.parametrize(
    ("python", "xml"),
    [
        (0, "0"),
        (-300, "-300"),
        (426822752000000, "426822752000000"),
        (0, "-0"),
        (12, XML_WHITESPACE + "12" + XML_WHITESPACE),
    ],
)
def test_parse_int(python, xml):
    """Convert to python.

    See https://datypic.com/sc/xsd/t-xsd_integer.html
    """
    xml = list2xml(["integer", xml])
    i = vInt.from_xcal(xml)
    assert i == python, f"Expected {i} == {python}."


@pytest.mark.parametrize(
    ("i", "xml"),
    [
        (0, "0"),
        (-300, "-300"),
        (426822752000000, "426822752000000"),
        (-0, "0"),
    ],
)
def test_serialize_int(i, xml):
    """Convert to python.

    See https://datypic.com/sc/xsd/t-xsd_integer.html
    """
    result = to_xcal(vInt(i, _validate_range=False))
    assert xml2list(result) == ["integer", xml]


@pytest.mark.parametrize(
    "invalid_xml_value", ["", " ", "INVALID", "-3E2.4", "12E", "3.0"]
)
def test_parsing_errors(invalid_xml_value):
    """This tests invalid examples and asserts the correct error."""
    xml = list2xml(["integer", invalid_xml_value])

    with pytest.raises(XCalParsingError) as error:
        vInt.from_xcal(xml)
    assert (
        error.value.args[0]
        == f"Expected xsd:integer, got {invalid_xml_value.strip()!r} in /integer."
    )
