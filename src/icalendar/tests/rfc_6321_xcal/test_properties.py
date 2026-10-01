from __future__ import annotations

import pytest

from icalendar.cal.event import Event
from icalendar.error import XCalParsingError
from icalendar.parser.xcal.base import InvalidParserState
from icalendar.parser.xcal.property import XCalPropertyParser
from icalendar.prop.broken import vBroken
from icalendar.tests.rfc_6321_xcal.common import list2xml


def test_parameters_parser_finds_out_if_nothing_is_consumed(mock):
    """We can end in an endless loop if a vProp is not working."""
    e = list2xml(["properties", ["x-prop", ["text", "mailto:jsmith@example.com"]]])
    parser = XCalPropertyParser(e, mock)  # mock does not consume anything
    with pytest.raises(InvalidParserState) as e:
        parser.parse_property()
    assert "did not consume any XML." in str(e.value)
    assert "Endless loop detected" in str(e.value)


def test_broken_property_remains_broken(events):
    """A broken property is properly passed through xCal serialization/deserialization."""
    event: Event = events.issue_464_invalid_rdate
    rdate = event["RDATE"]
    assert isinstance(rdate, vBroken)
    xcal = event.to_xcal()
    xevent = Event.from_xcal(xcal)[0]
    xrdate = xevent["RDATE"]
    assert isinstance(xrdate, vBroken)
    assert xrdate == rdate

    assert xrdate.property_name == "RDATE"
    assert xrdate.expected_type == "vDDDLists"
    assert isinstance(xrdate.parse_error, XCalParsingError)
