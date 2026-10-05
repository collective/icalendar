"""xCal parameter serialization and deserialization tests.

See https://datatracker.ietf.org/doc/html/rfc6321#section-3.5

.. note::

    At present, the Parameters store string values.
    There is a type given for these but there are only strings stored.


"""

from __future__ import annotations

from xml.etree.ElementTree import Element, fromstring, tostring

import pytest

from icalendar import Parameters
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal, xml2list


def test_skip_value_parameter():
    """The VALUE property parameter is not mapped to an xCal XML
    element.  Instead, the value type is handled by having different XML
    elements for each value, and these appear inside of property
    elements.  Thus, when converting from iCalendar to xCal, any "VALUE"
    property parameters are skipped."""
    params = Parameters()
    params["VALUE"] = "DATE-TIME"
    xcal_element = to_xcal(params, wrap=True)
    assert len(xcal_element) == 0  # No parameters elements


@pytest.mark.parametrize(("text"), [None, ""])
def test_emtpy_parameters_from_xcal(text):
    """An empty <parameters> element should produce an empty Parameters object."""
    xcal_element = Element("parameters")
    xcal_element.text = text
    params = Parameters.from_xcal(xcal_element)
    assert isinstance(params, Parameters)
    assert len(params) == 0


def _appendix(name) -> str:
    return f"See {name.lower()}param in https://datatracker.ietf.org/doc/html/rfc6321#appendix-A"


EMAIL_1 = "mailto:john.doe@example.org"
EMAIL_1_XML = f"<cal-address>{EMAIL_1}</cal-address>"
EMAIL_2 = ["mailto:jane.doe@example.org", "mailto:joe.bloggs@example.org"]
EMAIL_2_XML = (
    f"<cal-address>{EMAIL_2[0]}</cal-address><cal-address>{EMAIL_2[1]}</cal-address>"
)

mark_parameters = pytest.mark.parametrize(
    ("name", "value", "xcal", "message"),
    [
        pytest.param(
            "X-PARAM",
            "PT30M",
            "<x-param><unknown>PT30M</unknown></x-param>",
            "Unknown parameters. See https://datatracker.ietf.org/doc/html/rfc6321#section-5",
            id="unknown-parameter",
        ),
        pytest.param(
            "partstat",
            "NEEDS-ACTION",
            "<partstat><text>NEEDS-ACTION</text></partstat>",
            "Example from https://datatracker.ietf.org/doc/html/rfc6321#section-3.5",
            id="partstat-example",
        ),
        pytest.param(
            "altrep",
            "cid:part1.0001@example.org",
            "<altrep><uri>cid:part1.0001@example.org</uri></altrep>",
            _appendix("ALTREP"),
            id="altrep",
        ),
        pytest.param(
            "cn",
            "John Doe",
            "<cn><text>John Doe</text></cn>",
            _appendix("CN"),
            id="cn",
        ),
        pytest.param(
            "cutype",
            "INDIVIDUAL",
            "<cutype><text>INDIVIDUAL</text></cutype>",
            _appendix("CUTYPE"),
            id="cutype",
        ),
        pytest.param(
            "delegated-from",
            EMAIL_1,
            f"<delegated-from>{EMAIL_1_XML}</delegated-from>",
            _appendix("delfrom"),
            id="delegated-from",
        ),
        pytest.param(
            "delegated-from",
            EMAIL_2,
            f"<delegated-from>{EMAIL_2_XML}</delegated-from>",
            _appendix("delfrom"),
            id="delegated-from-multiple",
        ),
        pytest.param(
            "delegated-to",
            EMAIL_1,
            f"<delegated-to>{EMAIL_1_XML}</delegated-to>",
            _appendix("delto"),
            id="delegated-to",
        ),
        pytest.param(
            "delegated-to",
            EMAIL_2,
            f"<delegated-to>{EMAIL_2_XML}</delegated-to>",
            _appendix("delto"),
            id="delegated-to-multiple",
        ),
        pytest.param(
            "dir",
            "ldap://example.com:6666/o=ABC%20Industries,c=US???(cn=Jim%20Dolittle)",
            "<dir><uri>ldap://example.com:6666/o=ABC%20Industries,c=US???(cn=Jim%20Dolittle)</uri></dir>",
            _appendix("DIR"),
            id="dir",
        ),
        pytest.param(
            "encoding",
            "BASE64",
            "<encoding><text>BASE64</text></encoding>",
            _appendix("ENCODING"),
            id="encoding-base64",
        ),
        pytest.param(
            "encoding",
            "8BIT",
            "<encoding><text>8BIT</text></encoding>",
            _appendix("ENCODING"),
            id="encoding-8bit",
        ),
        pytest.param(
            "fmttype",
            "text/plain",
            "<fmttype><text>text/plain</text></fmttype>",
            _appendix("FMTTYPE"),
            id="fmttype",
        ),
        pytest.param(
            "fbtype",
            "FREE",
            "<fbtype><text>FREE</text></fbtype>",
            _appendix("FBTYPE"),
            id="fbtype",
        ),
        pytest.param(
            "language",
            "en-US",
            "<language><text>en-US</text></language>",
            _appendix("LANGUAGE"),
            id="language",
        ),
        pytest.param(
            "member",
            EMAIL_1,
            f"<member>{EMAIL_1_XML}</member>",
            _appendix("MEMBER"),
            id="member",
        ),
        pytest.param(
            "member",
            EMAIL_2,
            f"<member>{EMAIL_2_XML}</member>",
            _appendix("MEMBER"),
            id="member-multiple",
        ),
        pytest.param(
            "partstat",
            "TENTATIVE",
            "<partstat><text>TENTATIVE</text></partstat>",
            _appendix("PARTSTAT"),
            id="partstat",
        ),
        pytest.param(
            "range",
            "THISANDFUTURE",
            "<range><text>THISANDFUTURE</text></range>",
            _appendix("RANGE"),
            id="range",
        ),
        pytest.param(
            "related",
            "START",
            "<related><text>START</text></related>",
            _appendix("trigrel"),
            id="related-start",
        ),
        pytest.param(
            "reltype",
            "PARENT",
            "<reltype><text>PARENT</text></reltype>",
            _appendix("RELTYPE"),
            id="reltype",
        ),
        pytest.param(
            "role",
            "CHAIR",
            "<role><text>CHAIR</text></role>",
            _appendix("ROLE"),
            id="role",
        ),
        pytest.param(
            "rsvp",
            "TRUE",
            "<rsvp><boolean>true</boolean></rsvp>",
            _appendix("RSVP"),
            id="rsvp-true",
        ),
        pytest.param(
            "rsvp",
            "FALSE",
            "<rsvp><boolean>false</boolean></rsvp>",
            _appendix("RSVP"),
            id="rsvp-false",
        ),
        pytest.param(
            "sent-by",
            EMAIL_1,
            f"<sent-by>{EMAIL_1_XML}</sent-by>",
            _appendix("SENT-BY"),
            id="sent-by",
        ),
        pytest.param(
            "tzid",
            "Europe/Berlin",
            "<tzid><text>Europe/Berlin</text></tzid>",
            _appendix("TZID"),
            id="tzid",
        ),
    ],
)


@mark_parameters
def test_parameters_to_xcal(name, value, xcal, message):
    """Convert Parameters to xcal.

    Any unrecognized property parameter MUST be converted using the
    value type XML element IC:unknown, with its content set to the
    property parameter value text, treated as if it were a "TEXT"
    value or list of "TEXT" values. - :rfc:`6321`
    """
    params = Parameters({name: value})
    xcal_element = to_xcal(params)
    assert isinstance(xcal_element, Element)
    text = tostring(xcal_element, encoding="unicode")
    assert text.startswith("<parameters>")
    assert text.endswith("</parameters>")
    assert text[12:-13] == xcal, message


@mark_parameters
def test_parameters_from_xcal(name, value, xcal, message):
    """Parse Parameters from xcal."""
    xcal_element = fromstring(f"<parameters>{xcal}</parameters>")
    params = Parameters.from_xcal(xcal_element)
    assert isinstance(params, Parameters)
    assert name in params, (
        f"Expected parameter {name} not found in parsed Parameters: {params}."
    )
    assert params[name] == value, message
    assert len(params) == 1, "We only parse one element."


multiple_values_parameters = pytest.mark.parametrize(
    "parameter_name",
    [
        "delegated-to",
        "delegated-from",
        "member",
    ],
)


@multiple_values_parameters
def test_parse_mulitple_values(parameter_name):
    """Check the conversion of list value parameters.

    In [RFC5545], some parameters allow using a COMMA-separated list of
    values.
    """
    xml = list2xml(
        [
            "parameters",
            [
                parameter_name,
                ["cal-address", "mailto:jsmith@example.org"],
                ["cal-address", "mailto:jsmith@example.com"],
            ],
        ]
    )
    parameters = Parameters.from_xcal(xml)
    expected_value = ["mailto:jsmith@example.org", "mailto:jsmith@example.com"]
    assert parameters.get_multiple(parameter_name) == expected_value
    assert parameters[parameter_name] == expected_value


@multiple_values_parameters
def test_serialize_multiple_values(parameter_name):
    """Test that multiple_values turn up in the correct order."""
    parameters = Parameters(
        {parameter_name: ["mailto:jsmith@example.org", "mailto:jsmith@example.com"]}
    )
    xcal = to_xcal(parameters)
    result = xml2list(xcal)
    assert result == [
        "parameters",
        [
            parameter_name,
            ["cal-address", "mailto:jsmith@example.org"],
            ["cal-address", "mailto:jsmith@example.com"],
        ],
    ]


def test_get_multiple_absent():
    """Test get_multiple when the value does not exist."""
    parameters = Parameters()
    assert parameters.get_multiple("absent") == []


def test_get_multiple_one_value():
    """Test get_multiple when there is one value."""
    parameters = Parameters({"cn": "John"})
    assert parameters.get_multiple("cn") == ["John"]


def test_get_multiple_many_values():
    """Test get_multiple when there is a list of values."""
    parameters = Parameters({"delegated-to": EMAIL_2})
    assert parameters.get_multiple("delegated-to") == EMAIL_2


def test_parameters_only_serialize_if_they_have_content():
    """Empty parameters must not turn up."""
    parameters = Parameters()
    xcal = to_xcal(parameters, wrap=True)
    assert len(xcal) == 0
