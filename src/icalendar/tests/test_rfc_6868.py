"""This implemensts RFC 6868.

There are only some changes to parameters needed.
"""
import os
from typing import TYPE_CHECKING

import pytest

from icalendar.parser import rfc_6868_unescape

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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("^a", "^a"),
        ("^^", "^"),
        # ("^n", ),
        ("^'", '"'),
    ],
)
@pytest.mark.parametrize(
    "modify", [lambda x: x, lambda x: x*10, lambda x: f"asd{x}aaA^AA"]
)
def test_unescape(text, expected, modify):
    """Check unescaping."""
    result = rfc_6868_unescape(modify(text))
    assert result == modify(expected)


@pytest.mark.parametrize(
    "newline", ["\n", "\r\n", "\r", os.linesep])
def test_unescape_newline(newline, monkeypatch):
    """Unescape the newline."""
    monkeypatch.setattr(os, "linesep", newline)
    assert rfc_6868_unescape("^n") == newline
