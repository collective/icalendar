"""This code tests the behaviour of the XML parser we use."""

import pathlib

import pytest

from icalendar import Calendar, config
from icalendar.tests.rfc_6321_xcal.common import list2xml


def test_component_uses_xml_parser_result(monkeypatch, mock):
    """Make sure the XML parser is used."""
    monkeypatch.setattr(config, "parse_xml", mock)
    mock.return_value.getroot.return_value = list2xml(
        [
            "icalendar",
            [
                "vcalendar",
                [
                    "properties",
                    ["prodid", ["text", "-//Example Inc.//Example Client//EN"]],
                ],
            ],
        ]
    )

    parsed = Calendar.from_xcal(b"<icalendar></icalendar>")[0]
    assert parsed["PRODID"] == "-//Example Inc.//Example Client//EN"
    mock.assert_called_once()


HERE = pathlib.Path(__file__).parent
MAIN = HERE / "include" / "main.xml"


def test_include_is_not_processed():
    """XML include is not processed.

    Include is the only vilnerability that is listed in
    https://github.com/tiran/defusedxml/blob/c7445887f5e1bcea470a16f61369d29870cfcfe1/README.md#python-xml-libraries
    """
    etree = config.parse_xml(MAIN.open("rb"))
    root = etree.getroot()
    assert root[0].tag == "header"
    assert root[1].tag == "{http://www.w3.org/2001/XInclude}include"
    assert root[2].tag == "footer"


def test_default_parser_requires_a_read_attribute():
    """We make sure that people do not pass strings that are
    understood as paths.
    """
    with pytest.raises(TypeError) as e:
        config.parse_xml("string")

    assert "Expected source.read() method." in str(e.value)
