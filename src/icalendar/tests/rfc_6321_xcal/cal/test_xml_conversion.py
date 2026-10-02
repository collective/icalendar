"""Make sure we can also output pretty XML for xCal."""

import re
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from icalendar.cal.calendar import Calendar

# BEGIN:VCALENDAR
# VERSION:2.0
# PRODID:-//collective//icalendar//7.3.1.dev270//EN
# UID:664546b1-5828-49a9-adc5-80d108fb4f13
# END:VCALENDAR
MINIMAL_CALENDAR_XCAL_PRETTY = b"""<?xml version="1.0" encoding="UTF-8"?>
<icalendar xmlns="urn:ietf:params:xml:ns:icalendar-2.0">
  <vcalendar>
    <properties>
      <version>
        <text>2.0</text>
      </version>
      <prodid>
        <text>-//collective//icalendar//7.3.1.dev270//EN</text>
      </prodid>
      <uid>
        <text>664546b1-5828-49a9-adc5-80d108fb4f13</text>
      </uid>
    </properties>
  </vcalendar>
</icalendar>
"""


MINIMAL_CALENDAR_XCAL_SINGLE_LINE = re.sub(b"^\\s+", b"", MINIMAL_CALENDAR_XCAL_PRETTY)


def test_pretty_xml(calendars):
    cal: Calendar = calendars.minimal
    xml = cal.to_xcal(indent="  ")
    for i, (line1, line2) in enumerate(
        zip(
            xml.decode("utf-8").splitlines(),
            MINIMAL_CALENDAR_XCAL_PRETTY.decode("utf-8").splitlines(),
            strict=False,
        )
    ):
        assert line1 == line2, f"Line {i + 1} does not match"
    assert xml == MINIMAL_CALENDAR_XCAL_PRETTY


def test_single_line_xml(calendars):
    cal: Calendar = calendars.minimal
    xml = cal.to_xcal(indent=None)
    assert b"\n" not in xml
    print(xml)
    print(MINIMAL_CALENDAR_XCAL_SINGLE_LINE)
    assert xml == MINIMAL_CALENDAR_XCAL_SINGLE_LINE


def test_invalid_argument_for_stream(comp):
    """Check that invalid arguments for stream raise a TypeError."""
    with pytest.raises(TypeError):
        comp.to_xcal(3.14)
    with pytest.raises(TypeError):
        comp.to_xcal(object())


def test_invalid_argument_for_indent(comp):
    """Check that invalid arguments for indent raise a TypeError."""
    with pytest.raises(TypeError):
        comp.to_xcal(indent=3.14)
    with pytest.raises(TypeError):
        comp.to_xcal(indent=object())
