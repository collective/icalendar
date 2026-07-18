"""Duplicate TZID properties on VTIMEZONE must not crash parsing."""

from icalendar import Calendar


def test_from_ical_duplicate_vtimezone_tzid_uses_first():
    """Two TZID lines become a list; unknown first id must still parse."""
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//test//EN\r\n"
        "BEGIN:VTIMEZONE\r\n"
        "TZID:Custom/WeirdZone\r\n"
        "TZID:AlsoWeird\r\n"
        "BEGIN:STANDARD\r\n"
        "DTSTART:19700101T000000\r\n"
        "TZOFFSETFROM:+0000\r\n"
        "TZOFFSETTO:+0000\r\n"
        "END:STANDARD\r\n"
        "END:VTIMEZONE\r\n"
        "END:VCALENDAR\r\n"
    )
    cal = Calendar.from_ical(ics)
    vtimezone = cal.walk("VTIMEZONE")[0]
    assert vtimezone.tz_name == "Custom/WeirdZone"
