"""A globally unique TZID (:rfc:`5545#section-3.2.19`) must resolve its timezone.

Clients such as libical, Evolution and Mozilla Lightning emit the "globally
unique" TZID form ``/<vendor>/<Olson/Name>`` (for example
``/freeassociation.sourceforge.net/Europe/Berlin``). Previously the vendor
prefix stopped the timezone from being identified, so the value was parsed as
timezone-naive and the UTC offset was silently lost.

See https://github.com/collective/icalendar/issues/313
"""

from datetime import timedelta

import pytest

from icalendar.timezone import tzid_from_tzinfo

# UID -> (expected Olson name, expected UTC offset on 2020-04-26) for each event
# in ``calendars/issue_313_globally_unique_tzid.ics``.
EVENTS = {
    "libical-evolution@issue-313": ("Europe/Berlin", timedelta(hours=2)),
    "mozilla-lightning@issue-313": ("America/New_York", timedelta(hours=-4)),
    "multipart-olson@issue-313": (
        "America/Argentina/Buenos_Aires",
        timedelta(hours=-3),
    ),
}


def test_events_with_global_tzids_are_timezone_aware(calendars):
    """Every event resolves its globally unique TZID instead of going naive."""
    events = calendars.issue_313_globally_unique_tzid.walk("VEVENT")
    assert len(events) == len(EVENTS)
    for event in events:
        expected_tzid, expected_offset = EVENTS[str(event["UID"])]
        start = event["DTSTART"].dt
        assert start.tzinfo is not None
        assert start.utcoffset() == expected_offset
        assert tzid_from_tzinfo(start.tzinfo) == expected_tzid


@pytest.mark.parametrize(
    ("tzid", "resolved_tzid"),
    [
        # libical / Evolution: /<vendor>/<Olson/Name>
        ("/freeassociation.sourceforge.net/Europe/Berlin", "Europe/Berlin"),
        # libical Tzfile prefix in front of the Olson name
        ("/freeassociation.sourceforge.net/Tzfile/Europe/Paris", "Europe/Paris"),
        # Mozilla Lightning / Thunderbird: /<vendor>/<datestamp>/<Olson/Name>
        ("/mozilla.org/20070129_1/America/New_York", "America/New_York"),
        # Citadel: /<vendor>/<datestamp>/<Olson/Name>
        ("/citadel.org/20190914_1/Europe/Berlin", "Europe/Berlin"),
        # a single-component Olson name behind a vendor prefix
        ("/mozilla.org/20071231_1/UTC", "UTC"),
        # a multi-part Olson name behind a vendor prefix
        (
            "/vendor.example/America/Argentina/Buenos_Aires",
            "America/Argentina/Buenos_Aires",
        ),
        # a plain id without a vendor prefix keeps resolving
        ("Europe/Berlin", "Europe/Berlin"),
        # an unknown trailing identifier stays unresolved (no false positives)
        ("/vendor.example/Not/ARealZone", None),
    ],
)
def test_timezone_id_resolves(tzp, tzid, resolved_tzid):
    """The trailing Olson identifier is recovered regardless of prefix depth."""
    tz = tzp.timezone(tzid)
    if resolved_tzid is None:
        assert tz is None
    else:
        assert tzid_from_tzinfo(tz) == resolved_tzid
