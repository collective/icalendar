"""A globally unique TZID (:rfc:`5545#section-3.2.19`) must resolve its timezone.

Clients such as libical/Evolution emit the "globally unique" TZID form
``/<vendor>/<Olson/Name>`` (for example
``/freeassociation.sourceforge.net/Europe/Berlin``). Previously the vendor
prefix stopped the timezone from being identified, so the value was parsed as
timezone-naive and the UTC offset was silently lost.

See https://github.com/collective/icalendar/issues/313
"""

from datetime import timedelta

import pytest

from icalendar import Calendar
from icalendar.timezone import tzid_from_tzinfo

GLOBAL_BERLIN = "/freeassociation.sourceforge.net/Europe/Berlin"


def _event_ics(tzid: str) -> str:
    return (
        "BEGIN:VCALENDAR\r\n"
        "BEGIN:VEVENT\r\n"
        f"DTSTART;TZID={tzid}:20200426T140000\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )


def test_global_tzid_is_parsed_with_timezone(tzp):
    """The vendor-prefixed TZID resolves to Europe/Berlin, not a naive datetime."""
    calendar = Calendar.from_ical(_event_ics(GLOBAL_BERLIN))
    dt = calendar.walk("VEVENT")[0]["DTSTART"].dt
    assert dt.tzinfo is not None
    assert dt.utcoffset() == timedelta(hours=2)  # CEST on 2020-04-26
    assert tzid_from_tzinfo(dt.tzinfo) == "Europe/Berlin"


@pytest.mark.parametrize(
    "tz_id",
    [
        "/freeassociation.sourceforge.net/Europe/Berlin",
        "/citadel.org/20190914_1/Europe/Berlin",  # extra vendor path component
    ],
)
def test_timezone_resolves_global_prefix(tzp, tz_id):
    """The trailing Olson identifier is recovered regardless of prefix depth."""
    assert tzid_from_tzinfo(tzp.timezone(tz_id)) == "Europe/Berlin"


def test_timezone_resolves_multipart_olson_name(tzp):
    """Multi-part Olson names behind a vendor prefix still resolve."""
    tz = tzp.timezone("/vendor.example/America/Argentina/Buenos_Aires")
    assert tzid_from_tzinfo(tz) == "America/Argentina/Buenos_Aires"


def test_unknown_global_tzid_returns_none(tzp):
    """A globally unique id whose suffix is not a real timezone stays unresolved."""
    assert tzp.timezone("/vendor.example/Not/ARealZone") is None
