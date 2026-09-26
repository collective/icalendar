"""period conversion

https://datatracker.ietf.org/doc/html/rfc6321#section-3.6.9
"""

from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

import pytest

from icalendar import vPeriod
from icalendar.error import XCalParsingError

START = datetime(1997, 1, 1, 18, 0, 0, tzinfo=timezone.utc)
END = datetime(1997, 1, 2, 7, 0, 0, tzinfo=timezone.utc)
DURATION = timedelta(hours=5, minutes=30)

XML_END = (
    "<period><start>1997-01-01T18:00:00Z</start>"
    "<end>1997-01-02T07:00:00Z</end></period>"
)
XML_DURATION = (
    "<period><start>1997-01-01T18:00:00Z</start><duration>PT5H30M</duration></period>"
)

mark_values = pytest.mark.parametrize(
    ("value", "xml"),
    [
        (vPeriod((START, END)), XML_END),
        (vPeriod((START, DURATION)), XML_DURATION),
    ],
)


@mark_values
def test_to_xcal(value, xml):
    """Convert to xcal, keeping the form the period was written in."""
    e = value.to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "period"
    assert ET.tostring(e, encoding="unicode") == xml


@mark_values
def test_from_xcal(value, xml):
    """Parse from xcal."""
    result = vPeriod.from_xcal(ET.fromstring(xml))
    assert isinstance(result, vPeriod)
    assert result == value
    assert result.by_duration == value.by_duration


def test_a_missing_start_is_an_error():
    """A period must have a start."""
    e = ET.fromstring("<period><end>1997-01-02T07:00:00Z</end></period>")
    with pytest.raises(XCalParsingError) as error:
        vPeriod.from_xcal(e)
    assert error.value.parser == vPeriod


def test_a_missing_end_and_duration_is_an_error():
    """A period must have an end or a duration."""
    e = ET.fromstring("<period><start>1997-01-01T18:00:00Z</start></period>")
    with pytest.raises(XCalParsingError) as error:
        vPeriod.from_xcal(e)
    assert error.value.parser == vPeriod


@pytest.mark.parametrize(
    "xml",
    [
        "<period><start>INVALID</start><end>1997-01-02T07:00:00Z</end></period>",
        "<period><start>1997-01-01T18:00:00Z</start><end>INVALID</end></period>",
        "<period><start>1997-01-01T18:00:00Z</start><duration>INVALID</duration></period>",
    ],
)
def test_invalid_values_are_errors(xml):
    """The halves are parsed by vDatetime and vDuration."""
    with pytest.raises(XCalParsingError):
        vPeriod.from_xcal(ET.fromstring(xml))
