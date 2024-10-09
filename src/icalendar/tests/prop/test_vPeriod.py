import unittest
from datetime import datetime, timedelta

import pytest

from icalendar.prop import vPeriod


class TestProp(unittest.TestCase):
    def test_one_day(self):
        # One day in exact datetimes
        per = (datetime(2000, 1, 1), datetime(2000, 1, 2))
        self.assertEqual(vPeriod(per).to_ical(), b"20000101T000000/20000102T000000")

        per = (datetime(2000, 1, 1), timedelta(days=31))
        self.assertEqual(vPeriod(per).to_ical(), b"20000101T000000/P31D")

    def test_roundtrip(self):
        p = vPeriod.from_ical("20000101T000000/20000102T000000")
        self.assertEqual(p, (datetime(2000, 1, 1, 0, 0), datetime(2000, 1, 2, 0, 0)))
        self.assertEqual(vPeriod(p).to_ical(), b"20000101T000000/20000102T000000")

        self.assertEqual(
            vPeriod.from_ical("20000101T000000/P31D"),
            (datetime(2000, 1, 1, 0, 0), timedelta(31)),
        )

    def test_round_trip_with_absolute_time(self):
        p = vPeriod.from_ical("20000101T000000Z/20000102T000000Z")
        self.assertEqual(vPeriod(p).to_ical(), b"20000101T000000Z/20000102T000000Z")

    def test_bad_input(self):
        self.assertRaises(ValueError, vPeriod.from_ical, "20000101T000000/Psd31D")


def test_timezoned(tzp):
    start = tzp.localize(datetime(2000, 1, 1), "Europe/Copenhagen")
    end = tzp.localize(datetime(2000, 1, 2), "Europe/Copenhagen")
    per = (start, end)
    assert vPeriod(per).to_ical() == b"20000101T000000/20000102T000000"
    assert vPeriod(per).params["TZID"] == "Europe/Copenhagen"


def test_timezoned_with_timedelta(tzp):
    p = vPeriod(
        (tzp.localize(datetime(2000, 1, 1), "Europe/Copenhagen"), timedelta(days=31))
    )
    assert p.to_ical() == b"20000101T000000/P31D"


@pytest.mark.parametrize(
    "params",
    [
        ("20000101T000000", datetime(2000, 1, 2)),
        (datetime(2000, 1, 1), "20000102T000000"),
        (datetime(2000, 1, 2), datetime(2000, 1, 1)),
        (datetime(2000, 1, 2), timedelta(-1)),
    ],
)
def test_invalid_parameters(params):
    """The parameters are of wrong type or of wrong order."""
    with pytest.raises(ValueError):
        vPeriod(params)
