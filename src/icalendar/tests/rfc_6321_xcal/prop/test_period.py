"""Tests for xCal PERIOD parsing.

- end/duration
- UTC/timezone for both start and end

Example from RFC 6321:

    <period>
        <start>2011-05-17T12:00:00</start>
        <duration>P1H</duration>
    </period>
"""

from datetime import datetime, timedelta, timezone
from pprint import pprint

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vDDDLists, vDDDTypes, vPeriod
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal_list


class vDDDLists(vDDDLists):  # noqa: N801
    def __init__(self, period, params=None):
        """Replace the initialization to not unfold the tuple."""
        super().__init__([period] if isinstance(period, tuple) else period, params=None)


@pytest.fixture(params=[vPeriod, vDDDTypes, vDDDLists])
def v_period(request) -> type[vDDDLists | vDDDTypes | vPeriod]:
    """Fixture for vDatetime, vDDDTypes, and vDDDLists."""
    return request.param


@pytest.fixture(params=["Europe/Berlin", "Asia/Tokyo"])
def tzid(request) -> str | None:
    """Possible tzid values."""
    return request.param


START_FLOATING = (datetime(2011, 5, 17, 20, 59), "2011-05-17T20:59:00")
START_UTC = (datetime(2011, 5, 17, 20, 59, tzinfo=timezone.utc), "2011-05-17T20:59:00Z")

END_FLOATING = (datetime(2011, 5, 17, 21, 30), "2011-05-17T21:30:00")
END_UTC = (datetime(2011, 5, 17, 21, 30, tzinfo=timezone.utc), "2011-05-17T21:30:00Z")

DURATION_POSITIVE = (timedelta(days=1, hours=1), "P1DT1H")
DURATION_NEGATIVE = (timedelta(days=-1, hours=-1), "-P1DT1H")
DURATION_0 = (timedelta(days=0, hours=0), "P0D")

PERIODS_DURATION_UTC = [
    (START_UTC, DURATION_POSITIVE),
    (START_UTC, DURATION_0),
]
PERIODS_DURATION_FLOATING = [
    (START_FLOATING, DURATION_POSITIVE),
    (START_FLOATING, DURATION_0),
]
PERIODS_DURATION_INVALID = [
    (START_FLOATING, DURATION_NEGATIVE),
    (START_UTC, DURATION_NEGATIVE),
]
PERIODS_END_UTC = [
    (START_UTC, END_UTC),
]
PERIODS_END_FLOATING = [
    (START_FLOATING, END_FLOATING),
]


def spec2period(spec, v_period, tzp=None, tzid=None) -> vPeriod:
    """Return the vPeriod."""
    start = spec[0][0]
    end = spec[1][0]
    if tzp is not None:
        assert tzid is not None, "tzid and tzp both required."
        start = tzp.localize(start, tzid)
        if not isinstance(end, timedelta):
            end = tzp.localize(end, tzid)
    return v_period((start, end))


def spec2list(spec, tzid=None) -> list[str | list]:
    """Return the xml list spec for easy comparism."""
    period = [
        "period",
        ["start", spec[0][1]],
        ["duration" if "P" in spec[1][1] else "end", spec[1][1]],
    ]
    if tzid is None:
        return ["TEST", period]
    return [
        "TEST",
        [
            "parameters",
            [
                "tzid",
                [
                    "text",
                    tzid,
                ],
            ],
        ],
        period,
    ]


@pytest.mark.parametrize(
    "spec",
    PERIODS_DURATION_UTC
    + PERIODS_DURATION_FLOATING
    + PERIODS_END_UTC
    + PERIODS_END_FLOATING,
)
def test_to_xml(spec, v_period):
    """Convert period to xml without timezone."""
    p = spec2period(spec, v_period)
    expected = spec2list(spec)
    converted = to_xcal_list(p)
    assert expected == converted


@pytest.mark.parametrize("spec", PERIODS_DURATION_FLOATING + PERIODS_END_FLOATING)
def test_to_xml_with_timezone(spec, v_period, tzid, tzp):
    """Convert period to xml without timezone."""
    p = spec2period(spec, v_period, tzp, tzid)
    expected = spec2list(spec, tzid)
    converted = to_xcal_list(p)
    assert expected == converted


VALID_PERIODS = (
    PERIODS_DURATION_FLOATING
    + PERIODS_END_FLOATING
    + PERIODS_DURATION_UTC
    + PERIODS_END_UTC
)


@pytest.mark.parametrize("spec", VALID_PERIODS)
def test_from_xml(spec, v_period):
    """Convert period to xml without timezone."""
    expected = spec2period(spec, v_period)
    xml = list2xml(spec2list(spec))
    parsed = v_period.from_xcal(xml)
    assert expected == parsed


@pytest.mark.parametrize(
    "spec",
    PERIODS_DURATION_FLOATING + PERIODS_END_FLOATING,
)
def test_from_xml_with_timezone(spec, v_period, tzid, tzp):
    """Convert period to xml without timezone."""
    expected = spec2period(spec, v_period, tzp, tzid)
    xml = list2xml(spec2list(spec, tzid))
    parsed = v_period.from_xcal(xml)
    assert expected == parsed


@pytest.mark.parametrize("spec", PERIODS_DURATION_INVALID)
def test_negative_duration_raises_error(spec, v_period):
    """A negative duration is parsed but wrong."""
    xml = list2xml(spec2list(spec))
    with pytest.raises(XCalParsingError) as e:
        v_period.from_xcal(xml)
    assert (
        e.value.message
        == f"Expected positive duration, got {spec[1][1]!r} in /test/period[1]/duration[1]."
    )


@pytest.mark.parametrize("spec", VALID_PERIODS)
def test_period_without_start_raises_error(spec, v_period):
    """A period without a start errors."""
    xml_list = spec2list(spec)
    del xml_list[1][1]  # delete start
    pprint(xml_list)
    xml = list2xml(xml_list)
    with pytest.raises(XCalParsingError) as e:
        v_period.from_xcal(xml)
    assert e.value.message == "Expected <start> in /test/period[1]."


@pytest.mark.parametrize("spec", VALID_PERIODS)
def test_period_without_end_raises_error(spec, v_period):
    """A period without a end/duration errors."""
    xml_list = spec2list(spec)
    del xml_list[1][2]  # delete end/duration
    pprint(xml_list)
    xml = list2xml(xml_list)
    with pytest.raises(XCalParsingError) as e:
        v_period.from_xcal(xml)
    assert e.value.message == "Expected <end> or <duration> in /test/period[1]."
