"""This module identifies timezones.

Normally, timezones have ids.
This is a way to access the ids if you have a
datetime.tzinfo object.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import dateutil.tz.tz as tz

if TYPE_CHECKING:
    from datetime import datetime, tzinfo


def tzids_from_tzinfo(tzinfo: Optional[tzinfo]) -> tuple[str]:
    """Get several timezone ids if we can identify the timezone.

    >>> import zoneinfo
    >>> from icalendar.timezone.tzid import tzids_from_tzinfo
    >>> tzids_from_tzinfo(zoneinfo.ZoneInfo("Africa/Accra"))
    ('Africa/Accra',)
    >>> from dateutil.tz import gettz
    >>> tzids_from_tzinfo(gettz("Europe/Berlin"))
    ('Arctic/Longyearbyen', 'Atlantic/Jan_Mayen', 'Europe/Berlin', 'Europe/Budapest', 'Europe/Copenhagen', 'Europe/Oslo', 'Europe/Stockholm', 'Europe/Vienna')

    """ # The example might need to change if you recreate the lookup tree
    if tzinfo is None:
        return ()
    if hasattr(tzinfo, 'zone'):
        return (tzinfo.zone,)  # pytz implementation
    if hasattr(tzinfo, 'key'):
        return (tzinfo.key,)  # ZoneInfo implementation
    if isinstance(tzinfo, tz._tzicalvtz):
        return (tzinfo._tzid,)
    if isinstance(tzinfo, tz.tzstr):
        return (tzinfo._s,)
    return tuple(sorted(tzinfo2tzids(tzinfo)))


def tzid_from_tzinfo(tzinfo: Optional[tzinfo]) -> Optional[str]:
    """Retrieve the timezone id from the tzinfo object.

    Some timezones are equivalent.
    Thus, we might return one ID that is equivelant to others.
    """
    tzids = tzids_from_tzinfo(tzinfo)
    if "UTC" in tzids:
        return "UTC"
    if not tzids:
        return None
    return tzids[0]

def tzid_from_dt(dt: datetime) -> Optional[str]:
    """Retrieve the timezone id from the datetime object."""
    tzid = tzid_from_tzinfo(dt.tzinfo)
    if tzid is None:
        return dt.tzname()
    return tzid


def tzinfo2tzids(tzinfo: Optional[tzinfo]) -> set[str]:
    """We return the tzids for a certain tzinfo object.

    With different datetimes, we match
    (tzinfo.utcoffset(dt), tzinfo.tzname(dt))

    If we could identify the timezone, you will receive a tuple
    with at least one tzid. All tzids are equivalent which means
    that they describe the same timezone.

    You should get results with any timezone implementation if it is known.
    This one is especially useful for dateutil.

    In the following example, we can see that the timezone Africa/Accra
    is equivalent to many others.

    >>> import zoneinfo
    >>> from icalendar.timezone.tzid import tzinfo2tzids
    >>> "Europe/Berlin" in tzinfo2tzids(zoneinfo.ZoneInfo("Europe/Berlin"))
    True

    """ # The example might need to change if you recreate the lookup tree
    if tzinfo is None:
        return set()
    from icalendar.timezone.equivalent_timezone_ids_result import lookup

    while 1:
        if isinstance(lookup, set):
            return lookup
        dt, offset2lookup = lookup
        offset = tzinfo.utcoffset(dt)
        lookup = offset2lookup.get(offset)
        if lookup is None:
            return set()
    return set()

__all__ = ["tzid_from_tzinfo", "tzid_from_dt", "tzids_from_tzinfo"]
