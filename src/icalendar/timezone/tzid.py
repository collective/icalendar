"""This module identifies timezones.

Normally, timezones have ids.
This is a way to access the ids if you have a
datetime.tzinfo object.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .equivalent_timezone_ids import tzinfo2tzids

if TYPE_CHECKING:
    from datetime import datetime, tzinfo


def tzids_from_tzinfo(tzinfo: tzinfo) -> tuple[str]:
    """Get several timezone ids if we can identify the timezone.

    >>> import zoneinfo
    >>> from icalendar.timezone.tzid import tzids_from_tzinfo
    >>> tzids_from_tzinfo(zoneinfo.ZoneInfo("Africa/Accra"))
    ('Africa/Accra',)
    >>> from dateutil.tz import gettz
    >>> tzids_from_tzinfo(gettz("Africa/Accra"))
    ('Africa/Abidjan', 'Africa/Accra', 'Africa/Bamako', 'Africa/Banjul', 'Africa/Conakry', 'Africa/Dakar')

    """
    if hasattr(tzinfo, 'zone'):
        return (tzinfo.zone,)  # pytz implementation
    if hasattr(tzinfo, 'key'):
        return (tzinfo.key,)  # dateutil implementation, tzinfo.key  # ZoneInfo implementation
    return tzinfo2tzids(tzinfo)


def tzid_from_tzinfo(tzinfo: tzinfo) -> Optional[str]:
    """Retrieve the timezone id from the tzinfo object.

    Some timezones are equivalent.
    Thus, we might return one ID that is equivelant to others.
    """
    return (tzids_from_tzinfo(tzinfo) + (None,))[0]


def tzid_from_dt(dt: datetime) -> Optional[str]:
    """Retrieve the timezone id from the datetime object."""
    tzid = tzid_from_tzinfo(dt.tzinfo)
    if tzid is None:
        return dt.tzname()
    return tzid

__all__ = ["tzid_from_tzinfo", "tzid_from_dt", "tzids_from_tzinfo"]
