"""xCal parameter serialization and deserialization tests.

See https://datatracker.ietf.org/doc/html/rfc6321#section-3.5
"""

from xml.etree.ElementTree import Element, fromstring, tostring

import pytest

from icalendar import Calendar, Parameters


def test_skip_value_parameter():
    """The VALUE property parameter is not mapped to an xCal XML
    element.  Instead, the value type is handled by having different XML
    elements for each value, and these appear inside of property
    elements.  Thus, when converting from iCalendar to xCal, any "VALUE"
    property parameters are skipped."""
    params = Parameters()
    params["VALUE"] = "DATE-TIME"
    xcal_element = params.to_xcal()
    assert xcal_element.tag == "parameters"
    assert len(xcal_element) == 0  # No child elements


def test_set_value_parameter_from_xcal():
    """When converting from xCal into
    iCalendar, the appropriate "VALUE" property parameter MUST be
    included in the iCalendar property if the value type is not the
    default value type for that property.
    """
    pytest.xfail("Not implemented yet")


def test_empty_parameters_to_xcal():
    """An empty Parameters object should produce an empty <parameters> element."""
    params = Parameters()
    xcal_element = params.to_xcal()
    assert xcal_element.tag == "parameters"
    assert len(xcal_element) == 0  # No child elements


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
            True,
            "<rsvp><boolean>true</boolean></rsvp>",
            _appendix("RSVP"),
            id="rsvp-true",
        ),
        pytest.param(
            "rsvp",
            False,
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
    """Convert Parameters to xcal."""
    params = Parameters({name: value})
    xcal_element = params.to_xcal()
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


@pytest.mark.parametrize(
    ("event_index", "parameter_index", "expected_value"),
    [
        (
            0,
            0,
            [
                "attendee",
                {
                    "delegated-to": [
                        "mailto:jdoe@example.com",
                        "mailto:jqpublic@example.com",
                    ]
                },
                "cal-address",
                "mailto:jsmith@example.com",
            ],
        ),
        (
            0,
            1,
            [
                "attendee",
                {
                    "delegated-from": [
                        "mailto:jsmith@example.com",
                        "mailto:jdoe@example.com",
                    ]
                },
                "cal-address",
                "mailto:jdoe@example.com",
            ],
        ),
        (
            0,
            2,
            [
                "attendee",
                {
                    "member": [
                        "mailto:projectA@example.com",
                        "mailto:projectB@example.com",
                    ]
                },
                "cal-address",
                "mailto:janedoe@example.com",
            ],
        ),
        (
            1,
            0,
            [
                "attendee",
                {"delegated-to": "mailto:jdoe@example.com"},
                "cal-address",
                "mailto:jsmith@example.com",
            ],
        ),
        (
            1,
            1,
            [
                "attendee",
                {"delegated-from": "mailto:jsmith@example.com"},
                "cal-address",
                "mailto:jdoe@example.com",
            ],
        ),
        (
            1,
            2,
            [
                "attendee",
                {"member": "mailto:projectA@example.com"},
                "cal-address",
                "mailto:janedoe@example.com",
            ],
        ),
    ],
)
def test_parameters_with_values_as_list(
    calendars, event_index, parameter_index, expected_value
):
    """Check the conversion of list value parameters.

    In [RFC5545], some parameters allow using a COMMA-separated list of
    values.  To ease processing in jCal, the value of such parameters
    MUST be represented in an array containing the separated values.
    """
    pytest.xfail("Not implemented yet")
    calendar: Calendar = calendars.rfc_7256_multi_value_parameters
    event = calendar.events[event_index]
    parameter = event.to_xcal()[1][parameter_index]
    assert parameter == expected_value


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
