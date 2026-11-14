from xml.etree.ElementTree import Element, tostring

import pytest

from icalendar import vCalAddress
from icalendar.parser import Parameters


@pytest.mark.parametrize(
    ("attr", "tag"),
    [
        ("MEMBER", "member"),
        ("DELEGATED_TO", "delegated-to"),
        ("DELEGATED_FROM", "delegated-from"),
    ],
)
def test_attribute_parameter_xcal_serialization(attr, tag):
    """Setting MEMBER/DELEGATED-TO/DELEGATED-FROM via attributes serializes cleanly to xCal."""
    addr = vCalAddress("mailto:user@example.com")
    setattr(addr, attr, "mailto:target@example.com")

    element = Element("attendee")
    addr.to_xcal(element)
    xml_str = tostring(element).decode()

    assert (
        f"<{tag}><cal-address>mailto:target@example.com</cal-address></{tag}>"
        in xml_str
    )
    assert "tuple" not in xml_str
    assert "(" not in xml_str


@pytest.mark.parametrize(
    ("attr", "param_key"),
    [
        ("MEMBER", "member"),
        ("DELEGATED_TO", "delegated-to"),
        ("DELEGATED_FROM", "delegated-from"),
    ],
)
def test_attribute_parameter_jcal_serialization(attr, param_key):
    """Setting MEMBER/DELEGATED-TO/DELEGATED-FROM via attributes serializes cleanly to jCal."""
    addr = vCalAddress("mailto:user@example.com")
    setattr(addr, attr, "mailto:target@example.com")

    jcal_params = addr.params.to_jcal()
    assert jcal_params[param_key] == ["mailto:target@example.com"]


def test_multiple_values_as_tuple_xcal_and_jcal():
    """Tuple with multiple addresses serializes properly to xCal and jCal."""
    addr = vCalAddress("mailto:user@example.com")
    addr.MEMBER = ("mailto:group1@example.com", "mailto:group2@example.com")

    element = Element("attendee")
    addr.to_xcal(element)
    xml_str = tostring(element).decode()

    assert "<cal-address>mailto:group1@example.com</cal-address>" in xml_str
    assert "<cal-address>mailto:group2@example.com</cal-address>" in xml_str
    assert "(" not in xml_str

    jcal_params = addr.params.to_jcal()
    assert jcal_params["member"] == [
        "mailto:group1@example.com",
        "mailto:group2@example.com",
    ]


def test_parameters_get_multiple_handles_tuples_and_lists():
    """Parameters.get_multiple extracts list from both tuples and lists."""
    params = Parameters()
    params["MEMBER"] = ("mailto:a@example.com", "mailto:b@example.com")
    assert params.get_multiple("MEMBER") == [
        "mailto:a@example.com",
        "mailto:b@example.com",
    ]

    params["CN"] = "John Doe"
    assert params.get_multiple("CN") == ["John Doe"]

    assert params.get_multiple("ABSENT") == []
