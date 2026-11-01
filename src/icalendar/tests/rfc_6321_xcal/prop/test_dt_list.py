"""Some attributes contain a few more entries and go into vDDDList.

To test:
- RDATE with date/date-time/utc/tzid
- EXDATE with date/date-time/utc/tzid
- RDATE with period

"""

from datetime import date, datetime, time, timedelta

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt.list import vDDDLists
from icalendar.prop.dt.types import vDDDTypes
from icalendar.tests.rfc_6321_xcal.common import list2xml
from icalendar.timezone.tzid import tzid_from_dt


@pytest.mark.parametrize(
    ("xml", "values", "tz"),
    [
        (
            [
                "exdate",
                ["date-time", "2021-01-01T00:00:01"],
                ["date-time", "2021-01-01T00:00:02"],
                ["date-time", "2021-01-01T00:00:03"],
            ],
            [
                datetime(2021, 1, 1, 0, 0, 1),
                datetime(2021, 1, 1, 0, 0, 2),
                datetime(2021, 1, 1, 0, 0, 3),
            ],
            None,
        ),
        (
            [
                "exdate",
                ["date-time", "2021-01-01T00:00:01Z"],
                ["date-time", "2021-01-01T00:00:02Z"],
                ["date-time", "2021-01-01T00:00:03Z"],
            ],
            [
                datetime(2021, 1, 1, 0, 0, 1),
                datetime(2021, 1, 1, 0, 0, 2),
                datetime(2021, 1, 1, 0, 0, 3),
            ],
            "UTC",
        ),
        (
            [
                "exdate",
                ["parameters", ["tzid", ["text", "Europe/Vienna"]]],
                ["date-time", "2021-01-01T00:00:01"],
                ["date-time", "2021-01-01T00:00:02"],
                ["date-time", "2021-01-01T00:00:03"],
            ],
            [
                datetime(2021, 1, 1, 0, 0, 1),
                datetime(2021, 1, 1, 0, 0, 2),
                datetime(2021, 1, 1, 0, 0, 3),
            ],
            "Europe/Vienna",
        ),
        (
            [
                "exdate",
                ["date", "2021-01-01"],
                ["date", "2021-01-02"],
                ["date", "2021-01-03"],
            ],
            [
                date(2021, 1, 1),
                date(2021, 1, 2),
                date(2021, 1, 3),
            ],
            None,
        ),
        (
            [
                "rdate",
                [
                    "period",
                    ["start", "2021-01-01T00:00:01"],
                    ["end", "2021-01-01T00:00:02"],
                ],
                [
                    "period",
                    ["start", "2021-01-01T00:00:02"],
                    ["end", "2021-02-01T00:00:02"],
                ],
                [
                    "period",
                    ["start", "2021-01-01T00:00:03"],
                    ["end", "2021-03-01T00:00:02"],
                ],
            ],
            [
                (datetime(2021, 1, 1, 0, 0, 1), datetime(2021, 1, 1, 0, 0, 2)),
                (datetime(2021, 1, 1, 0, 0, 2), datetime(2021, 2, 1, 0, 0, 2)),
                (datetime(2021, 1, 1, 0, 0, 3), datetime(2021, 3, 1, 0, 0, 2)),
            ],
            None,
        ),
        (
            [
                "rdate",
                [
                    "period",
                    ["start", "2021-01-01T00:00:01Z"],
                    ["end", "2021-01-01T00:00:02Z"],
                ],
                [
                    "period",
                    ["start", "2021-01-01T00:00:02Z"],
                    ["end", "2021-02-01T00:00:02Z"],
                ],
                [
                    "period",
                    ["start", "2021-01-01T00:00:03Z"],
                    ["end", "2021-03-01T00:00:02Z"],
                ],
            ],
            [
                (datetime(2021, 1, 1, 0, 0, 1), datetime(2021, 1, 1, 0, 0, 2)),
                (datetime(2021, 1, 1, 0, 0, 2), datetime(2021, 2, 1, 0, 0, 2)),
                (datetime(2021, 1, 1, 0, 0, 3), datetime(2021, 3, 1, 0, 0, 2)),
            ],
            "UTC",
        ),
        (
            [
                "rdate",
                ["parameters", ["tzid", ["text", "Europe/Berlin"]]],
                [
                    "period",
                    ["start", "2021-01-01T00:00:01"],
                    ["end", "2021-01-01T00:00:02"],
                ],
                [
                    "period",
                    ["start", "2021-01-01T00:00:02"],
                    ["end", "2021-02-01T00:00:02"],
                ],
            ],
            [
                (datetime(2021, 1, 1, 0, 0, 1), datetime(2021, 1, 1, 0, 0, 2)),
                (datetime(2021, 1, 1, 0, 0, 2), datetime(2021, 2, 1, 0, 0, 2)),
            ],
            "Europe/Berlin",
        ),
        (
            [
                "x-prop",
                ["parameters", ["tzid", ["text", "Europe/Berlin"]]],
                ["time", "00:01:01"],
                ["time", "00:01:02"],
                ["time", "00:01:03"],
                ["time", "00:01:04"],
            ],
            [
                time(0, 1, 1),
                time(0, 1, 2),
                time(0, 1, 3),
                time(0, 1, 4),
            ],
            "Europe/Berlin",
        ),
        (
            [
                "x-prop",
                ["time", "00:01:01Z"],
                ["time", "00:01:02Z"],
                ["time", "00:01:03Z"],
                ["time", "00:01:04Z"],
            ],
            [
                time(0, 1, 1),
                time(0, 1, 2),
                time(0, 1, 3),
                time(0, 1, 4),
            ],
            "UTC",
        ),
        (
            [
                "x-prop",
                ["time", "00:01:01"],
                ["time", "00:01:02"],
                ["time", "00:01:03"],
                ["time", "00:01:04"],
            ],
            [
                time(0, 1, 1),
                time(0, 1, 2),
                time(0, 1, 3),
                time(0, 1, 4),
            ],
            None,
        ),
        (
            [
                "x-prop",
                ["duration", "P1D"],
                ["duration", "P2D"],
                ["duration", "P3D"],
                ["duration", "P4D"],
            ],
            [
                timedelta(days=1),
                timedelta(days=2),
                timedelta(days=3),
                timedelta(days=4),
            ],
            None,
        ),
    ],
)
def test_get_all_values_from_element(xml, values, tz, tzp):
    """Make sure that all values are parsed."""
    dd = vDDDLists.from_xcal(list2xml(xml))
    tzs = [get_tz(d) for d in dd.dts]
    assert tzs == [tz] * len(values)
    assert [no_tz(d.dt) for d in dd.dts] == values


def no_tz(v):
    """Remove the timezone for comparism"""
    if isinstance(v, tuple):
        return no_tz(v[0]), no_tz(v[1])
    if isinstance(v, (time, datetime)):
        return v.replace(tzinfo=None)
    return v


def get_tz(e: vDDDTypes) -> str | None:
    """Get the tzid"""
    t = e.dt
    if isinstance(t, tuple):
        t = t[0]
    if isinstance(t, (time, datetime)):
        return tzid_from_dt(t)
    return None


MARK_ORDER = pytest.mark.parametrize(
    "dts",
    [
        [
            ["date-time", "2021-01-01T00:00:00Z"],
            ["date-time", "2021-01-01T00:00:00"],
        ],
        [
            ["date-time", "2021-01-01T00:00:00"],
            ["date-time", "2021-01-01T00:00:00Z"],
        ],
        [
            ["date-time", "2021-01-01T00:00:00"],
            ["date-time", "2021-01-01T00:00:00"],
            ["date-time", "2021-01-01T00:00:00Z"],
        ],
        [
            ["date-time", "2021-01-01T00:00:00"],
            ["date-time", "2021-01-01T00:00:00Z"],
            ["date-time", "2021-01-01T00:00:00"],
        ],
        [
            ["date-time", "2021-01-01T00:00:00Z"],
            ["date-time", "2021-01-01T00:00:00"],
            ["date-time", "2021-01-01T00:00:00"],
        ],
    ],
)


@MARK_ORDER
def test_cannot_mix_utc_and_floating_datetimes(dts):
    with pytest.raises(
        XCalParsingError, match=r"Cannot mix floating with UTC in /x-prop\."
    ):
        vDDDLists.from_xcal(
            list2xml(
                [
                    "x-prop",
                ]
                + dts
            )
        )


@MARK_ORDER
def test_cannot_mix_utc_and_tzid_datetimes(dts):
    with pytest.raises(
        XCalParsingError,
        match=r"Cannot mix Asia/Singapore with UTC in /x-prop/date-time\[\d\]\.",
    ):
        vDDDLists.from_xcal(
            list2xml(
                [
                    "x-prop",
                    ["parameters", ["tzid", ["text", "Asia/Singapore"]]],
                ]
                + dts
            )
        )


@MARK_ORDER
def test_cannot_mix_utc_and_floating_times(dts):
    with pytest.raises(
        XCalParsingError, match=r"Cannot mix floating with UTC in /x-prop\."
    ):
        vDDDLists.from_xcal(
            list2xml(
                [
                    "x-prop",
                ]
                + [["time", v[1][11:]] for v in dts]
            )
        )


@MARK_ORDER
def test_cannot_mix_utc_and_tzid_times(dts):
    with pytest.raises(
        XCalParsingError,
        match=r"Cannot mix Asia/Singapore with UTC in /x-prop/time\[\d\]\.",
    ):
        vDDDLists.from_xcal(
            list2xml(
                [
                    "x-prop",
                    ["parameters", ["tzid", ["text", "Asia/Singapore"]]],
                ]
                + [["time", v[1][11:]] for v in dts]
            )
        )


def test_get_empty_dts():
    """We should not error if empty"""
    assert vDDDLists.from_xcal(list2xml(["x-prop"])).dts == []
