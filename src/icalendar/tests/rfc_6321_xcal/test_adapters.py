"""Test the adapters and convenience methods."""

from xml.etree.ElementTree import Element, SubElement

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


def test_root_xpath():
    e = Element("root")
    a = ElementAdapter(e)
    assert a.get_xpath() == "/root"


def test_child_xpath():
    e = Element("root")
    SubElement(e, "child")
    SubElement(e, "child")
    SubElement(e, "child")
    SubElement(e, "other-child")
    a = ElementAdapter(e)
    assert a.get_xpath() == "/root"
    children = a.children
    assert children[0].get_xpath() == "/root/child[1]"
    assert children[1].get_xpath() == "/root/child[2]"
    assert children[2].get_xpath() == "/root/child[3]"
    assert children[3].get_xpath() == "/root/other-child[1]"


def test_string():
    e = Element("root")
    SubElement(e, "child")
    a = ElementAdapter(e)
    assert str(a) == "Element@/root"
    assert str(a.children[0]) == "Element@/root/child[1]"
