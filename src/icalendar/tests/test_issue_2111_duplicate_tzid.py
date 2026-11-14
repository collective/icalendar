from icalendar import Calendar


def test_duplicate_tzid_in_vtimezone_does_not_crash():
    """Duplicate TZID in VTIMEZONE should not crash with AttributeError.

    See https://github.com/collective/icalendar/issues/2111
    """
    ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//EN
BEGIN:VTIMEZONE
TZID:Europe/Berlin
TZID:Europe/Berlin
BEGIN:STANDARD
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
TZNAME:CET
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
END:STANDARD
END:VTIMEZONE
END:VCALENDAR
"""
    cal = Calendar.from_ical(ics)
    assert len(cal.timezones) == 1
    assert cal.timezones[0].tz_name == "Europe/Berlin"
