"""
Test for GitHub issue #1238:
X-properties with VALUE=<type> should be parsed using that type,
not fall back to vUnknown.
"""
import pytest
from icalendar import Calendar
from icalendar.prop.dt import vPeriod


@pytest.mark.parametrize(("cal_str", "prop_name", "expected_type"), [
    (
        "BEGIN:VCALENDAR\r\nX-FILTER-DATE-RANGE;VALUE=PERIOD:20250202T000000/20250203T000000\r\nEND:VCALENDAR\r\n",
        "X-FILTER-DATE-RANGE",
        vPeriod,
    ),
])

def test_x_property_respects_value_param(cal_str, prop_name, expected_type):
    """X-properties with a VALUE parameter should be parsed as that type (issue #1238)."""
    calendar = Calendar.from_ical(cal_str)
    result = calendar[prop_name]
    assert isinstance(result, expected_type), (
        f"Expected {expected_type.__name__}, got {type(result).__name__}"
    )