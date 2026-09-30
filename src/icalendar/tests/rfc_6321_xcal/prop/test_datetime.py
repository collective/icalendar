"""date-time converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.4
"""

from datetime import datetime, timezone
from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vDatetime, vDDDLists, vDDDTypes
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal, xml2list
from icalendar.timezone.tzid import tzid_from_dt


@pytest.fixture(params=[vDatetime, vDDDTypes, vDDDLists])
def v_datetime(request):
    """Fixture for vDatetime, vDDDTypes, and vDDDLists."""
    return request.param


mark_values = pytest.mark.parametrize(
    ("date", "xcal"),
    [
        (datetime(2011, 5, 17, 20, 59), "2011-05-17T20:59:00"),
        (datetime(2025, 11, 10, 0, 0, 10, tzinfo=timezone.utc), "2025-11-10T00:00:10Z"),
    ],
)


@mark_values
def test_to_xcal(v_datetime, date, xcal):
    """Convert to xcal."""
    e = to_xcal(v_datetime(date))
    assert isinstance(e, ET.Element)
    assert e.tag == "date-time"
    assert e.text == xcal
    assert ET.tostring(e, encoding="unicode") == f"<date-time>{xcal}</date-time>"


@mark_values
def test_from_xcal_from_dt_class(v_datetime, date, xcal):
    """Parse from xcal."""
    e = list2xml(["x-prop", ["date-time", xcal]])
    result = v_datetime.from_xcal(e)
    assert result.dt == date


@pytest.mark.parametrize(
    ("xcal"),
    [
        "INVALID",
        "2025-1110",  # TODO: Be less strict if it is unambigious
        "2025111",
        "2025-11-10T00:0010",
        "2025111A",
    ],
)
def test_invalid_value_from_xcal(v_datetime, xcal):
    """Parse from xcal with invalid value."""
    e = list2xml(["x-prop", ["date-time", xcal]])
    with pytest.raises(XCalParsingError) as error:
        v_datetime.from_xcal(e)
    assert (
        error.value.message
        == f"Expected date-time format YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SSZ, got {xcal!r} in /x-prop/date-time[1]."
    )


mark_floating_datetime = pytest.mark.parametrize(
    "dt", [datetime(2025, 11, 10, 0, 0, 10), datetime(1997, 1, 31, 23, 59, 59)]
)
mark_timezone = pytest.mark.parametrize("tz", ["Asia/Tokyo", "Europe/Paris"])


@mark_floating_datetime
@mark_timezone
def test_datetime_to_xcal_includes_timezone(tzp, dt, tz, v_datetime):
    """Convert to xcal."""
    v_dt = v_datetime(tzp.localize(dt, tz))
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
            "date-time",
            dt.strftime("%Y-%m-%dT%H:%M:%S"),
        ],
    ]
    result = xml2list(e)
    assert result == expected


@mark_floating_datetime
@mark_timezone
def test_xcal_to_datetime_considers_timezone(tzp, dt, tz, v_datetime):
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
                "date-time",
                dt.strftime("%Y-%m-%dT%H:%M:%S"),
            ],
        ]
    )
    v_dt = v_datetime.from_xcal(xml)
    assert v_dt.dt.replace(tzinfo=None) == dt
    assert tzid_from_dt(v_dt.dt) == tz
