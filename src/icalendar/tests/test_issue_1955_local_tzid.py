"""Local timezone definitions can differ between calendars. See :issue:`1955`."""

from datetime import datetime, timedelta, timezone

import pytest

from icalendar import Calendar, Event, LazyCalendar, Timezone, TimezoneStandard


@pytest.mark.parametrize("calendar_class", [Calendar, LazyCalendar])
@pytest.mark.parametrize("forward_reference", [False, True])
def test_local_tzid_uses_current_calendar_definition(
    tzp, calendar_class, forward_reference
):
    """Reusing a TZID must not reuse another calendar's timezone definition."""
    starts = []
    for hours in (1, 2, 1):
        standard = TimezoneStandard()
        standard.DTSTART = datetime(1970, 1, 1)
        standard.TZOFFSETFROM = standard.TZOFFSETTO = timedelta(hours=hours)
        zone = Timezone()
        zone.add("tzid", "Local-Office")
        zone.add_component(standard)
        event = Event.new(
            uid=f"calendar-{hours}@example.org",
            stamp=datetime(2007, 1, 1, tzinfo=timezone.utc),
        )
        event.add(
            "dtstart", datetime(2007, 1, 2, 12), parameters={"TZID": "Local-Office"}
        )
        components = [event, zone] if forward_reference else [zone, event]
        calendar = Calendar.new(subcomponents=components)
        parsed = calendar_class.from_ical(calendar.to_ical())
        starts.append(parsed.events[0].start)

    assert [start.astimezone(timezone.utc) for start in starts] == [
        datetime(2007, 1, 2, hour, tzinfo=timezone.utc) for hour in (11, 10, 11)
    ]
