"""This implemensts RFC 6868.

There are only some changes to parameters needed.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from icalendar import Calendar, vCalAddress


def test_rfc_6868_example(calendars):
    """Check the example from the RFC."""
    cal : Calendar = calendars.rfc_6868
    attendee : vCalAddress = cal.events[0]["attendee"]
    assert attendee.name == 'George Herman "Babe" Ruth'


def test_all_parameters(calendars):
    """Check that all examples get decoded correctly."""
    cal : Calendar = calendars.rfc_6868
    param = cal["X-PARAM"].params["ALL"]
    assert param == '^"\n'


def test_unknown_character(calendars):
    """if a ^ (U+005E) character is followed by any character other than
      the ones above, parsers MUST leave both the ^ and the following
      character in place"""
    cal : Calendar = calendars.rfc_6868
    param = cal["X-PARAM"].params["UNKNOWN"]
    assert param == "^a^ ^asd"
