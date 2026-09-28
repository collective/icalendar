"""time converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.4
"""

from datetime import time, timezone
from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vDDDLists, vDDDTypes, vTime
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal, xml2list
from icalendar.timezone.tzid import tzid_from_dt


@pytest.fixture(params=[vTime, vDDDTypes, vDDDLists])
def v_time(request):
    """Fixture for vTime, vDDDTypes, and vDDDLists."""
    return request.param


mark_values = pytest.mark.parametrize(
    ("time_value", "xcal"),
    [
        (time(23, 59), "23:59:00"),
        (time(0, 0, 10, tzinfo=timezone.utc), "00:00:10Z"),
    ],
)


@mark_values
def test_to_xcal(v_time, time_value, xcal):
    """Convert to xcal."""
    e = to_xcal(v_time(time_value))
    assert isinstance(e, ET.Element)
    assert e.tag == "time"
    assert e.text == xcal
    assert ET.tostring(e, encoding="unicode") == f"<time>{xcal}</time>"


@mark_values
def test_from_xcal_from_dt_class(v_time, time_value, xcal):
    """Parse from xcal."""
    e = list2xml(["x-prop", ["time", xcal]])
    result = v_time.from_xcal(e)
    assert result.dt == time_value


@pytest.mark.parametrize(
    ("xcal"),
    [
        "INVALID",
        "1:1:1",  # TODO: Be less strict if it is unambigious
        "2025111",
        "2025-11-10T00:0010",
        "2025111A",
    ],
)
def test_invalid_value_from_xcal(v_time, xcal):
    """Parse from xcal with invalid value."""
    e = list2xml(["x-prop", ["time", xcal]])
    with pytest.raises(XCalParsingError) as error:
        v_time.from_xcal(e)
    assert (
        error.value.message
        == f"Expected time format HH:MM:SS or HH:MM:SSZ, got {xcal!r} in /x-prop/time[1]."
    )


mark_time = pytest.mark.parametrize("time_value", [time(0, 0, 10), time(23, 59, 59)])
mark_timezone = pytest.mark.parametrize("tz", ["Asia/Tokyo", "Europe/Paris"])


@mark_time
@mark_timezone
def test_time_to_xcal_includes_timezone(tzp, time_value: time, tz, v_time):
    """Convert to xcal."""
    v_dt = v_time(tzp.localize(time_value, tz))
    e = to_xcal(v_dt, wrap=True)
    expected = [
        "TEST",
        [
            "parameters",
            [
                "tzid",
                [
                    "text",
                    tz,
                ],
            ],
        ],
        [
            "time",
            time_value.strftime("%H:%M:%S"),
        ],
    ]
    result = xml2list(e)
    assert result == expected


@mark_time
@mark_timezone
def test_xcal_to_time_considers_timezone(tzp, time_value: time, tz, v_time):
    """Test that the timezone is considered when parsing."""
    xml = list2xml(
        [
            "dtstart",
            [
                "parameters",
                [
                    "tzid",
                    [
                        "text",
                        tz,
                    ],
                ],
            ],
            [
                "time",
                time_value.strftime("%H:%M:%S"),
            ],
        ]
    )
    v_dt = v_time.from_xcal(xml)
    assert v_dt.dt.replace(tzinfo=None) == time_value
    assert tzid_from_dt(v_dt.dt) == tz
