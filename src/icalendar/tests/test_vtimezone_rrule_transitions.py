"""A VTIMEZONE RRULE must repeat yearly.

Timezones created from a VTIMEZONE expand its RRULE from DTSTART.
An RRULE such as FREQ=SECONDLY could exhaust memory or CPU.
"""

import dateutil.rrule
import pytest

from icalendar import vRecur

# Far more than any test here needs, small enough to stop in seconds.
MAX_EXPANDED_TRANSITIONS = 10_000


@pytest.fixture(autouse=True)
def bounded_rrule_expansion(monkeypatch):
    """Fail fast instead of hanging if an RRULE is expanded without a limit."""
    expand = dateutil.rrule.rrule._iter

    def bounded_expand(self):
        for count, dt in enumerate(expand(self)):
            if count >= MAX_EXPANDED_TRANSITIONS:
                pytest.fail(
                    f"RRULE expanded to more than {MAX_EXPANDED_TRANSITIONS} transitions"
                )
            yield dt

    monkeypatch.setattr(dateutil.rrule.rrule, "_iter", bounded_expand)


SECONDLY_ICAL = "pr_2047_vtimezone_secondly_rrule_ical.ics"
SECONDLY_JCAL = "pr_2047_vtimezone_secondly_rrule_jcal.jcal"
SECONDLY_XCAL = "pr_2047_vtimezone_secondly_rrule_xcal.xml"


def test_secondly_rrule_from_1970_is_invalid(calendars):
    """Reading the offset of an event in a SECONDLY timezone fails fast.

    Without the check, this exhausts memory.
    """
    with pytest.raises(ValueError, match="FREQ=YEARLY"):
        calendars[SECONDLY_ICAL].events[0].DTSTART.utcoffset()


@pytest.mark.parametrize("source", [SECONDLY_ICAL, SECONDLY_JCAL, SECONDLY_XCAL])
@pytest.mark.parametrize("method", ["to_tz", "get_transitions"])
def test_secondly_rrule_is_invalid_in_all_formats(calendars, tzp, source, method):
    """iCalendar, jCal and xCal reject the timezone."""
    with pytest.raises(ValueError, match="FREQ=YEARLY"):
        timezone = calendars[source].timezones[0]
        if method == "to_tz":
            timezone.to_tz(tzp, lookup_tzid=False)
        else:
            timezone.get_transitions()


@pytest.mark.parametrize(
    "freq", ["SECONDLY", "MINUTELY", "HOURLY", "DAILY", "WEEKLY", "MONTHLY"]
)
def test_rrule_that_does_not_repeat_yearly_is_invalid(timezones, tzp, freq):
    """Only a yearly RRULE is valid in a timezone."""
    timezone = timezones.pacific_fiji
    timezone.standard[0]["RRULE"] = vRecur.from_ical(f"FREQ={freq}")
    with pytest.raises(ValueError, match="FREQ=YEARLY"):
        timezone.to_tz(tzp, lookup_tzid=False)
    with pytest.raises(ValueError, match="FREQ=YEARLY"):
        timezone.get_transitions()


def test_yearly_rrule_is_used(timezones, tzp):
    """A yearly RRULE with BYxxx parts still works."""
    assert timezones.pacific_fiji.to_tz(tzp, lookup_tzid=False) is not None
