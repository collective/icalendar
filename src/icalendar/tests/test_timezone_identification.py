"""Test that we can identify all timezones."""

import pytest
try:
    from zoneinfo import ZoneInfo, available_timezones
except ImportError:
    from backports.zoneinfo import ZoneInfo, available_timezones

from icalendar.timezone import tzids_from_tzinfo, tzid_from_tzinfo

tzids = available_timezones() - {"Factory", "localtime"}
with_tzid = pytest.mark.parametrize("tzid", tzids)

@with_tzid
def test_can_identify_zoneinfo(tzid, zoneinfo_only):
    """Check that all those zoneinfo timezones can be identified."""
    assert tzid in tzids_from_tzinfo(ZoneInfo(tzid))

@with_tzid
def test_can_identify_pytz(tzid, pytz_only):
    """Check that all those pytz timezones can be identified."""
    import pytz
    assert tzid in tzids_from_tzinfo(pytz.timezone(tzid))

@with_tzid
def test_can_identify_dateutil(tzid):
    """Check that all those dateutil timezones can be identified."""
    from dateutil.tz import gettz
    assert tzid in tzids_from_tzinfo(gettz(tzid))

def test_utc_is_identified(utc):
    """Test UTC because it is handled in a special way."""
    assert "UTC" in tzids_from_tzinfo(utc)
    assert tzid_from_tzinfo(utc) == "UTC"
