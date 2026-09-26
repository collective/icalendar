"""recur conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.10
"""

from xml.etree import ElementTree as ET

import pytest

from icalendar import vRecur
from icalendar.error import XCalParsingError

mark_values = pytest.mark.parametrize(
    ("ical", "xml"),
    [
        ("FREQ=DAILY;COUNT=10", "<recur><freq>DAILY</freq><count>10</count></recur>"),
        (
            "FREQ=YEARLY;UNTIL=20250101T000000Z;BYDAY=-1SU,MO;BYMONTH=10",
            "<recur><freq>YEARLY</freq><until>2025-01-01T00:00:00Z</until>"
            "<byday>-1SU</byday><byday>MO</byday><bymonth>10</bymonth></recur>",
        ),
        (
            "FREQ=WEEKLY;UNTIL=20250101;INTERVAL=2;WKST=SU",
            "<recur><freq>WEEKLY</freq><until>2025-01-01</until>"
            "<interval>2</interval><wkst>SU</wkst></recur>",
        ),
    ],
)


@mark_values
def test_to_xcal(ical, xml):
    """Convert to xcal: one element per value, in the canonical order."""
    e = vRecur.from_ical(ical).to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "recur"
    assert ET.tostring(e, encoding="unicode") == xml


@mark_values
def test_from_xcal(ical, xml):
    """Parse from xcal."""
    result = vRecur.from_xcal(ET.fromstring(xml))
    assert isinstance(result, vRecur)
    assert result == vRecur.from_ical(ical)
    assert result.to_ical().decode() == ical


def test_an_empty_recur_is_an_error():
    """A recurrence rule must have at least one rule part."""
    with pytest.raises(XCalParsingError) as error:
        vRecur.from_xcal(ET.fromstring("<recur></recur>"))
    assert error.value.parser == vRecur


@pytest.mark.parametrize(
    "xml",
    [
        "<recur><freq>DAILY</freq><count>NOT-A-NUMBER</count></recur>",
        "<recur><freq>DAILY</freq><bymonth>NOPE</bymonth></recur>",
    ],
)
def test_an_invalid_rule_part_is_an_error(xml):
    """The rule parts are parsed by their own value types."""
    with pytest.raises(XCalParsingError) as error:
        vRecur.from_xcal(ET.fromstring(xml))
    assert error.value.parser == vRecur
