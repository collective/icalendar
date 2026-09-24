"""CATEGORIES converison

https://datatracker.ietf.org/doc/html/rfc6321#appendix-A
-> # 3.8.1.2 Categories

<categories><text>Work</text><text>Meeting</text></categories>
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vCategory
from icalendar.prop.factory import TypesFactory
from icalendar.tests.rfc_6321_xcal.common import to_xcal


@pytest.mark.parametrize(
    ("category"),
    [
        vCategory([]),
        vCategory(["a"]),
        vCategory(["a", "b"]),
    ],
)
def test_to_xcal(category):
    """Convert to xcal."""
    e = to_xcal(category, wrap=True)
    assert len(e) == len(category.cats)
    for c, e in zip(category.cats, e, strict=True):
        assert e.tag == "text"
        assert e.text == c


@pytest.mark.parametrize(
    ("cats"),
    [
        [],  # empty is not allowed according the the spec, yet we still process it
        ["a"],
        ["a", "b"],
    ],
)
def test_from_xcal(types_factory: TypesFactory, cats):
    """Parse from xcal."""
    e = ET.Element("categories")
    for cat in cats:
        e.append(ET.Element("text"))
        e[-1].text = cat
    expected = vCategory(cats)
    result = types_factory.parse_xcal_property(e)
    print(repr(result))
    assert isinstance(result, vCategory)
    assert result == expected


def test_empty_value_should_not_fail():
    """Parse from xcal with empty value.

    That could also fail but then with the correct error.
    Consistency: We do not check formatting of these addresses.
    """
    e = ET.Element("categories")
    result = vCategory.from_xcal(e)
    assert isinstance(result, vCategory)
    assert result == vCategory([])
