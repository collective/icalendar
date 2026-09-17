"""float converison

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.2
https://datypic.com/sc/xsd/t-xsd_float.html
"""

import math
from xml.etree import ElementTree as ET

import pytest

from icalendar import vFloat
from icalendar.error import XCalParsingError
from icalendar.prop.factory import TypesFactory

from .common import XML_WHITESPACE


@pytest.mark.parametrize(
    ("python", "xml", "message"),
    [
        (0.0, "0", ""),
        (-300.0, "-3E2", ""),
        (426822752000000.0, "4268.22752E11", ""),
        (+24.3e-3, "+24.3e-3", ""),
        (12.0, "12", ""),
        (3.5, "+3.5", "any value valid for decimal is also valid for float"),
        (-float("inf"), "-INF", "negative infinity"),
        (0.0, "-0", "0"),
        (float("nan"), "NaN", "Not a Number"),
        (12, XML_WHITESPACE + "12" + XML_WHITESPACE, "White Space: collapse"),
    ],
)
def test_xsd_float_to_python(python, xml, message):
    """Convert to python.

    See https://datypic.com/sc/xsd/t-xsd_float.html
    """
    converted = vFloat.from_xsd_float(xml)
    is_nan = math.isnan(converted) and xml.lower() == "nan"
    assert converted == python or is_nan, (
        f"Expected {converted} == {python}. " + message
    )


@pytest.mark.parametrize(
    ("python", "xml", "message"),
    [
        (0.0, "0.0", ""),
        (-300.0, "-300.0", ""),
        (4268.22752e11, "426822752000000.0", ""),
        (+24.3e-3, "0.0243", ""),
        (12.0, "12.0", ""),
        (3.5, "3.5", ""),
        (12000000000000000000.0, "1.2e+19", "python example"),
        (-float("inf"), "-INF", "negative infinity"),
        (float("-inf"), "-INF", "infinity"),
        (float("nan"), "NaN", "Not a Number"),
    ],
)
def test_python_to_xsd(python, xml, message):
    """Convert to xds:float.

    See https://datypic.com/sc/xsd/t-xsd_float.html
    """
    converted = vFloat.to_xsd_float(python)
    is_nan = math.isnan(python) and converted.lower() == "nan"
    assert converted == xml or is_nan, f"Expected {converted!r} == {xml!r}. " + message


@pytest.mark.parametrize(
    "invalid_xml_value", ["", " ", "INVALID", "-3E2.4", "12E", None]
)
def test_parsing_errors(invalid_xml_value):
    """This tests invalid examples and asserts the correct error.

    Excluded from https://datypic.com/sc/xsd/t-xsd_float.html:
    - NAN
    """
    with pytest.raises((TypeError, ValueError)) as error:
        vFloat.from_xsd_float(invalid_xml_value)
    assert error.value.args[0] == f"Expected xsd:float. Got {invalid_xml_value!r}."


mark_values = pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1000.1234", vFloat(1000.1234)),
        ("-INF", vFloat(float("-inf"))),
    ],
)


@mark_values
def test_to_xcal(value, expected):
    """Convert to xcal."""
    e = expected.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "float"
    assert e.text == value
    assert ET.tostring(e, encoding="unicode") == f"<float>{value}</float>"


@mark_values
def test_from_xcal(types_factory: TypesFactory, value, expected):
    """Parse from xcal."""
    e = ET.Element("float")
    e.text = value
    result = types_factory.from_xcal("x-prop", e)
    assert isinstance(result, vFloat)
    assert result == expected


def test_invalid_value_from_xcal(types_factory: TypesFactory):
    """Parse from xcal with invalid value."""
    e = ET.Element("float")
    e.text = "INVALID"
    with pytest.raises(XCalParsingError) as error:
        types_factory.from_xcal("x-prop", e)
    assert error.value.parser == vFloat
    assert (
        error.value.message
        == "Expected xsd:float. Got 'INVALID' in 'float' element parsing 'vFloat'."
    )
