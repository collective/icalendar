"""Test that we can identify all timezones.

Timezones can be removed from ./timezone_ids.py if they make the tests fail:
Timezone information changes over time and can be dependent on the operating system's
timezone database (zoneinfo, dateutil) or the package (pytz).
We want to make sure we can roughly identify most of them.
"""

from icalendar.timezone import tzid_from_tzinfo, tzids_from_tzinfo
from icalendar.timezone.tzp import TZP


def test_can_identify_zoneinfo(tzid, zoneinfo_only, tzp:TZP):
    """Check that all those zoneinfo timezones can be identified."""
    assert tzid in tzids_from_tzinfo(tzp.timezone(tzid))


def test_can_identify_pytz(tzid, pytz_only, tzp:TZP):
    """Check that all those pytz timezones can be identified."""
    assert tzid in tzids_from_tzinfo(tzp.timezone(tzid))


def test_can_identify_dateutil(tzid):
    """Check that all those dateutil timezones can be identified."""
    from dateutil.tz import gettz
    assert tzid in tzids_from_tzinfo(gettz(tzid))


def test_utc_is_identified(utc):
    """Test UTC because it is handled in a special way."""
    assert "UTC" in tzids_from_tzinfo(utc)
    assert tzid_from_tzinfo(utc) == "UTC"
