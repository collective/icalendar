"""A VTIMEZONE RRULE with too many transitions is invalid.

Timezones created from a VTIMEZONE expand its RRULE from DTSTART.
A frequent RRULE could exhaust memory or CPU.
"""

from datetime import datetime

import pytest

import icalendar.config as cfg
from icalendar import Calendar, Timezone

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:{tzid}
BEGIN:STANDARD
DTSTART:20370101T000000
RRULE:{rrule}
TZOFFSETFROM:+0100
TZOFFSETTO:+0000
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:20370601T000000
RRULE:FREQ=YEARLY
TZOFFSETFROM:+0000
TZOFFSETTO:+0100
END:DAYLIGHT
END:VTIMEZONE
"""

CALENDAR = """BEGIN:VCALENDAR
{vtimezone}BEGIN:VEVENT
UID:transitions
DTSTART;TZID={tzid}:20370701T120000
END:VEVENT
END:VCALENDAR
"""


def calendar(tzid: str, rrule: str) -> str:
    vtimezone = VTIMEZONE.format(tzid=tzid, rrule=rrule)
    return CALENDAR.format(vtimezone=vtimezone, tzid=tzid).replace("\n", "\r\n")


@pytest.mark.parametrize(
    "rrule",
    [
        "FREQ=SECONDLY",
        "FREQ=MINUTELY",
        "FREQ=HOURLY",
        "FREQ=DAILY",
        "FREQ=YEARLY;BYMONTH=1,2,3,4,5,6,7,8,9,10,11,12;BYHOUR=0,1,2,3,4,5,6,7,8,9",
    ],
)
def test_frequent_rrule_is_invalid(tzp, rrule):
    """Parsing a VTIMEZONE with too many transitions fails fast."""
    tzid = f"transitions-{tzp.name}-{rrule}"
    with pytest.raises(ValueError, match="transitions within a year"):
        Calendar.from_ical(calendar(tzid, rrule))


@pytest.mark.parametrize("rrule", ["FREQ=YEARLY", "FREQ=MONTHLY", "FREQ=WEEKLY"])
def test_rrule_within_limit_is_used(tzp, rrule):
    """Timezones with few transitions a year still work."""
    tzid = f"transitions-{tzp.name}-{rrule}"
    event = Calendar.from_ical(calendar(tzid, rrule)).events[0]
    assert event.DTSTART == datetime(2037, 7, 1, 12, tzinfo=event.DTSTART.tzinfo)
    assert event.DTSTART.tzinfo is not None


def test_limit_can_be_disabled(tzp, monkeypatch):
    """Trusted input can use more transitions."""
    monkeypatch.setattr(cfg, "MAX_TIMEZONE_TRANSITIONS_PER_YEAR", -1)
    vtimezone = VTIMEZONE.format(tzid="transitions-disabled", rrule="FREQ=DAILY")
    timezone = Timezone.from_ical(vtimezone.replace("\n", "\r\n"))
    assert timezone.to_tz(tzp, lookup_tzid=False) is not None
