"""
Test for GitHub issue #1238:
X-properties with VALUE=<type> should be parsed using that type,
not fall back to vUnknown.
"""

from datetime import datetime

from icalendar import Calendar
from icalendar.prop.broken import vBroken
from icalendar.prop.dt import vPeriod


def test_x_property_respects_value_param(calendars):
    """X-properties with a VALUE parameter are parsed as the correct type (issue #1238)."""
    calendar = calendars.issue_1238
    result = calendar["X-FILTER-DATE-RANGE"]
    assert isinstance(result, vPeriod), f"Expected vPeriod, got {type(result).__name__}"
    assert result.start == datetime(2025, 2, 2, 0, 0)
    assert result.end == datetime(2025, 2, 3, 0, 0)


def test_x_property_broken_value():
    """X-properties with VALUE=PERIOD but invalid content should yield vBroken (issue #1238)."""

    cal_str = "BEGIN:VCALENDAR\r\nX-FILTER-DATE-RANGE;VALUE=PERIOD:this-is-not-a-period\r\nEND:VCALENDAR\r\n"

    calendar = Calendar.from_ical(cal_str)

    result = calendar["X-FILTER-DATE-RANGE"]
    assert isinstance(result, vBroken)
    assert str(result) == "this-is-not-a-period"
    assert result.expected_type == "vPeriod"
