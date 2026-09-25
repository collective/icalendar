"""Test the adapters and convenience methods."""

from xml.etree.ElementTree import Element

import pytest

from icalendar.parser.xcal.adapter import ElementAdapter


@pytest.mark.parametrize(
    "string", ["text", "中文鍵盤/中文键盘", "\\r\nText    \nwith\nnewlines   \t\n"]
)
def test_xsd_string_preserves_whitespace(string):
    e = Element("tag")
    e.text = string
    a = ElementAdapter(e)
    assert a.get_xsd_string() == string


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("   text  and more", "text and more"),
        ("\r\nText \\r   \nwith\nnewlines   \t\n", "Text \\r with newlines"),
    ],
)
def test_xsd_token_collapses_whitespace(string, expected):
    e = Element("tag")
    e.text = string
    a = ElementAdapter(e)
    assert a.get_xsd_token() == expected
