"""Generate VTIMEZONE components from actual timezone information.

When we generate VTIMEZONE from actual tzinfo instances of
- dateutil
- zoneinfo
- pytz

Then, we cannot assume that the future information stays the same but
we should be able to create tests that work for the past.
"""

from datetime import date, timedelta
from pprint import pprint
import pytest

from icalendar import Component, Timezone

tzids = pytest.mark.parametrize("tzid", [
    # "Europe/Berlin",
    "Asia/Singapore",
    # "America/New_York",
])

def assert_components_equal(c1:Component, c2:Component):
    """Print the diff of two components."""
    ML = 32
    ll1 = c1.to_ical().decode().splitlines()
    ll2 = c2.to_ical().decode().splitlines()
    pad = max(len(l) for l in ll1 if len(l) <=ML)
    diff = 0
    for l1, l2 in zip(ll1, ll2):
        a = len(l1) > 32 or len(l2) > 32
        print(a * "  " + l1, " " * (pad - len(l1)), a* "\n->" + l2, " "*(pad - len(l2)), "\tdiff!" if l1 != l2 else "")
        diff += l1 != l2
    assert not diff, f"{diff} lines differ"

@tzids
def test_conversion_converges(tzp, tzid):
    """tzinfo -> VTIMEZONE -> tzinfo -> VTIMEZONE

    We can assume that both generated VTIMEZONEs are equivalent.
    """
    tzinfo1 = tzp.timezone(tzid)
    assert tzinfo1 is not None
    generated1 = Timezone.from_tzinfo(tzinfo1)
    generated1["TZID"] = "test-generated"  # change the TZID so we do not use an existing one
    tzinfo2 = generated1.to_tz()
    generated2 = Timezone.from_tzinfo(tzinfo2, "test-generated")
    pprint(generated1.get_transitions())
    pprint(generated2.get_transitions())
    assert_components_equal(generated1, generated2)
    assert 2 <= len(generated1.standard + generated1.daylight) <= 3
    assert 2 <= len(generated2.standard + generated2.daylight) <= 3
    assert dict(generated1) == dict(generated2)
    assert generated1.to_ical().decode() == generated2.to_ical().decode()
    # assert generated1.daylight == generated2.daylight
    # assert generated1.standard == generated2.standard
    # assert generated1 == generated2
    assert False


@tzids
def both_tzps_generate_the_same_info(tzid, tzp):
    """We want to make sure that we get the same info for all timezone implementations.

    We assume that
    - the timezone implementations have the same info within the days we test
    - the timezone transitions times do not change because they are before last_date
    """
    # default generation
    tz1 = Timezone.from_tzid(tzid, tzp, last_date=date(2024, 1, 1))
    tzp.use_zoneinfo() # we compare to zoneinfo
    tz2 = Timezone.from_tzid(tzid, tzp, last_date=date(2024, 1, 1))
    assert_components_equal(tz1, tz2)
    assert tz1 == tz2


@tzids
def test_tzid_matches(tzid, tzp):
    """Check the TZID."""
    tz =  Timezone.from_tzinfo(tzp.timezone(tzid))
    assert tz["TZID"] == tzid


def test_do_not_convert_utc():
    """We do not need to convert UTC."""
    pytest.skip("TODO")


def test_berlin_time(tzp):
    """Test the Europe/Berlin timezone conversion."""
    tz = Timezone.from_tzid("Europe/Berlin")
    # we should have two timezones in it
    for x in tz.standard:
        print(x.name, x["TZNAME"], x["TZOFFSETFROM"].td, x["TZOFFSETTO"].td)
        print(x.to_ical().decode())
    assert len(tz.daylight) == 1
    assert len(tz.standard) in (1, 2), "We start in winter"
    dst = tz.daylight[-1]
    sta = tz.standard[-1]
    assert dst["TZNAME"] == "CEST"  # summer
    assert sta["TZNAME"] == "CET"
    assert dst["TZOFFSETFROM"].td == timedelta(hours=1)  # summer
    assert sta["TZOFFSETFROM"].td == timedelta(hours=2)
    assert dst["TZOFFSETTO"].td == timedelta(hours=2)  # summer
    assert sta["TZOFFSETTO"].td == timedelta(hours=1)


def test_end_of_zoninfo_range():pytest.skip("TODO")
def test_range_is_not_crossed():pytest.skip("TODO")


@tzids
def test_use_the_original_timezone(tzid, tzp):
    """When we get the timezone again, usually, we should use the
    one of the library/tzp."""
    tzinfo1 = tzp.timezone(tzid)
    assert tzinfo1 is not None
    generated1 = Timezone.from_tzinfo(tzinfo1)
    tzinfo2 = generated1.to_tz()
    assert type(tzinfo1) == type(tzinfo2)
    assert tzinfo1 == tzinfo2


@tzids
def test_offset_and_other_parameters_match(tzp, tzid):
    """When we create our timezone and parse it again
    we want to make sure that the generated times and their
    attributes match.
    - equality
    - utc offset
    - dst
    """
    pytest.skip("todo")
