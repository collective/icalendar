"""This tests the switch to different timezone implementations.

These are mostly located in icalendar.timezone.
"""

try:
    import pytz

    from icalendar.timezone.pytz import PYTZ
except ImportError:
    pytz = None
import copy
import pickle
from datetime import datetime, timedelta

import pytest
from dateutil.rrule import MONTHLY, rrule
from dateutil.tz.tz import _tzicalvtz

from icalendar import Calendar, LazyCalendar
from icalendar.prop import vDDDTypes
from icalendar.timezone.zoneinfo import ZONEINFO, zoneinfo

if pytz:
    PYTZ_TIMEZONES = pytz.all_timezones
    TZP_ = [PYTZ(), ZONEINFO()]
    NEW_TZP_NAME = ["pytz", "zoneinfo"]
else:
    PYTZ_TIMEZONES = []
    TZP_ = [ZONEINFO()]
    NEW_TZP_NAME = ["zoneinfo"]


@pytest.mark.parametrize(
    "tz_name", PYTZ_TIMEZONES + list(zoneinfo.available_timezones())
)
@pytest.mark.parametrize("tzp_", TZP_)
def test_timezone_names_are_known(tz_name, tzp_):
    """Make sure that all timezones are understood."""
    if tz_name in ("Factory", "localtime"):
        pytest.skip()
    assert tzp_.knows_timezone_id(tz_name), (
        f"{tzp_.__class__.__name__} should know {tz_name}"
    )


@pytest.mark.parametrize("func", [pickle.dumps, copy.copy, copy.deepcopy])
@pytest.mark.parametrize(
    "obj",
    [
        _tzicalvtz("id"),
        rrule(freq=MONTHLY, count=4, dtstart=datetime(2028, 10, 1), cache=True),
    ],
)
def test_can_pickle_timezone(func, tzp, obj):
    """Check that we can serialize and copy timezones."""
    func(obj)


def test_copied_rrule_is_the_same():
    """When we copy an rrule, we want it to be the same after this."""
    r = rrule(freq=MONTHLY, count=4, dtstart=datetime(2028, 10, 1), cache=True)
    assert str(copy.deepcopy(r)) == str(r)


def test_tzp_properly_switches(tzp, tzp_name):
    """We want the default implementation to switch."""
    assert (tzp_name == "pytz") == tzp.uses_pytz()


def test_tzp_is_pytz_only(tzp, tzp_name, pytz_only):
    """We want the default implementation to switch."""
    assert tzp_name == "pytz"
    assert tzp.uses_pytz()


def test_cache_reuse_timezone_cache(tzp, timezones):
    """Make sure we do not cache the timezones twice and change them."""
    tzp.cache_timezone_component(timezones.pacific_fiji)
    tzp1 = tzp.timezone("custom_Pacific/Fiji")
    assert tzp1 is tzp.timezone("custom_Pacific/Fiji")
    tzp.cache_timezone_component(timezones.pacific_fiji)
    assert tzp1 is tzp.timezone("custom_Pacific/Fiji"), "Cache is not replaced."


CALENDAR_WITH_CUSTOM_TZID = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:test
{}
END:VCALENDAR
"""
VTIMEZONE_WITH_OFFSET = """BEGIN:VTIMEZONE
TZID:{tzid}
BEGIN:STANDARD
DTSTART:16010101T000000
TZOFFSETFROM:{offset}
TZOFFSETTO:{offset}
END:STANDARD
END:VTIMEZONE"""
VEVENT_WITH_TZID = """BEGIN:VEVENT
UID:event
DTSTART;TZID={tzid}:20260601T100000
END:VEVENT"""


@pytest.mark.parametrize("forward_reference", [False, True])
def test_calendar_uses_its_own_vtimezone(tzp, forward_reference):
    """A VTIMEZONE cached from another calendar must not replace a calendar's own.

    The other calendar defines the same custom TZID with a different offset.
    """
    tzid = f"custom_Own/Definition_{forward_reference}"

    def calendar(offset):
        vtimezone = VTIMEZONE_WITH_OFFSET.format(tzid=tzid, offset=offset)
        vevent = VEVENT_WITH_TZID.format(tzid=tzid)
        components = [vevent, vtimezone] if forward_reference else [vtimezone, vevent]
        return CALENDAR_WITH_CUSTOM_TZID.format("\n".join(components))

    Calendar.from_ical(calendar("-1100"))
    start = Calendar.from_ical(calendar("+0200")).events[0].start
    assert start.utcoffset() == timedelta(hours=2)


@pytest.mark.parametrize(
    ("calendar_class", "forward_reference"),
    [
        (Calendar, False),
        pytest.param(
            Calendar,
            True,
            marks=pytest.mark.xfail(
                strict=True,
                reason="The forward reference re-parse uses one cache for all calendars.",
            ),
        ),
        (LazyCalendar, False),
        (LazyCalendar, True),
    ],
)
def test_calendars_in_one_file_use_their_own_vtimezone(
    tzp, calendar_class, forward_reference
):
    """Each calendar read with multiple=True uses its own VTIMEZONE."""
    tzid = f"custom_Own/Multiple_{calendar_class.__name__}_{forward_reference}"

    def calendar(offset):
        vtimezone = VTIMEZONE_WITH_OFFSET.format(tzid=tzid, offset=offset)
        vevent = VEVENT_WITH_TZID.format(tzid=tzid)
        components = [vevent, vtimezone] if forward_reference else [vtimezone, vevent]
        return CALENDAR_WITH_CUSTOM_TZID.format("\n".join(components))

    calendars = calendar_class.from_ical(
        calendar("-1100") + calendar("+0200"), multiple=True
    )
    offsets = [calendar.events[0].start.utcoffset() for calendar in calendars]
    assert offsets == [timedelta(hours=-11), timedelta(hours=2)]


@pytest.mark.parametrize("new_tzp_name", NEW_TZP_NAME)
def test_cache_is_emptied_when_tzp_is_switched(tzp, timezones, new_tzp_name):
    """Make sure we do not reuse the timezones created when we switch the provider."""
    tzp.cache_timezone_component(timezones.pacific_fiji)
    tz1 = tzp.timezone("custom_Pacific/Fiji")
    tzp.use(new_tzp_name)
    tzp.cache_timezone_component(timezones.pacific_fiji)
    tz2 = tzp.timezone("custom_Pacific/Fiji")
    assert tz1 is not tz2


def test_invalid_name(tzp):
    """Check that the provider name is OK."""
    provider = "invalid_provider"
    with pytest.raises(ValueError) as e:
        tzp.use(provider)
    # f"Unknown provider {provider}. Use 'pytz' or 'zoneinfo'."
    message = e.value.args[0]
    assert f"Unknown provider {provider}." in message
    assert "zoneinfo" in message
    assert "pytz" in message


@pytest.mark.parametrize(
    ("value", "expected_offset"),
    [
        ("19970101", timedelta(hours=-5)),  # EST
        ("19970701", timedelta(hours=-4)),  # EDT
    ],
)
def test_a_date_with_a_tzid_uses_the_offset_of_that_date(tzp, value, expected_offset):
    """A date is localized like a date-time, whichever provider is in use.

    pytz timezones default to their oldest offset, the local mean time one,
    until they are localized.
    """
    tzid = "America/New_York"
    midnight = datetime.strptime(value, "%Y%m%d")  # noqa: DTZ007
    offset = vDDDTypes.from_ical(value, timezone=tzid).utcoffset()
    # what the timezone database says about midnight on that date
    assert offset == midnight.replace(tzinfo=zoneinfo.ZoneInfo(tzid)).utcoffset()
    # what the same value written as a date-time is read as
    assert offset == vDDDTypes.from_ical(f"{value}T000000", timezone=tzid).utcoffset()
    assert offset == expected_offset
