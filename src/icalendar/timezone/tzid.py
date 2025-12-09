"""This module identifies timezones.

Normally, timezones have ids.
This is a way to access the ids if you have a
datetime.tzinfo object.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dateutil.tz import tz

from icalendar.timezone import equivalent_timezone_ids_result

if TYPE_CHECKING:
    from datetime import datetime, tzinfo

DATEUTIL_UTC = tz.gettz("UTC")
DATEUTIL_UTC_PATH: str | None = getattr(DATEUTIL_UTC, "_filename", None)
DATEUTIL_ZONEINFO_PATH = (
    None if DATEUTIL_UTC_PATH is None else Path(DATEUTIL_UTC_PATH).parent
)


def tzids_from_tzinfo(tzinfo: tzinfo | None) -> tuple[str]:
    """Get several timezone ids if we can identify the timezone.

    >>> import zoneinfo
    >>> from icalendar.timezone.tzid import tzids_from_tzinfo
    >>> tzids_from_tzinfo(zoneinfo.ZoneInfo("Arctic/Longyearbyen"))
    ('Arctic/Longyearbyen', 'Atlantic/Jan_Mayen', 'Europe/Berlin', 'Europe/Budapest', 'Europe/Copenhagen', 'Europe/Oslo', 'Europe/Stockholm', 'Europe/Vienna')
    >>> from dateutil.tz import gettz
    >>> tzids_from_tzinfo(gettz("Europe/Berlin"))
    ('Europe/Berlin', 'Arctic/Longyearbyen', 'Atlantic/Jan_Mayen', 'Europe/Budapest', 'Europe/Copenhagen', 'Europe/Oslo', 'Europe/Stockholm', 'Europe/Vienna')

    """  # The example might need to change if you recreate the lookup tree  # noqa: E501
    if tzinfo is None:
        return ()
    if hasattr(tzinfo, "zone"):
        return get_equivalent_tzids(tzinfo.zone)  # pytz implementation
    if hasattr(tzinfo, "key"):
        return get_equivalent_tzids(tzinfo.key)  # ZoneInfo implementation
    if isinstance(tzinfo, tz._tzicalvtz):  # noqa: SLF001
        return get_equivalent_tzids(tzinfo._tzid)  # noqa: SLF001
    if isinstance(tzinfo, tz.tzstr):
        return get_equivalent_tzids(tzinfo._s)  # noqa: SLF001
    if hasattr(tzinfo, "_filename"):  # dateutil.tz.tzfile  # noqa: SIM102
        if DATEUTIL_ZONEINFO_PATH is not None:
            # tzfile('/usr/share/zoneinfo/Europe/Berlin')
            path = tzinfo._filename  # noqa: SLF001
            if path.startswith(str(DATEUTIL_ZONEINFO_PATH)):
                tzid = str(Path(path).relative_to(DATEUTIL_ZONEINFO_PATH))
                return get_equivalent_tzids(tzid)
            return get_equivalent_tzids(path)
    if isinstance(tzinfo, tz.tzutc):
        return get_equivalent_tzids("UTC")

    # Fallback: try to identify timezone by behavior (utcoffset at different times)
    # This is needed for dateutil timezones that don't have easily accessible names
    # or when the filename approach doesn't work
    try:
        matching_tzids = _identify_tzid_by_behavior(
            tzinfo, equivalent_timezone_ids_result.lookup
        )
        if matching_tzids:
            # Return all equivalent timezone IDs for the first match
            first_tzid = next(iter(matching_tzids))
            return get_equivalent_tzids(first_tzid)
    except (ValueError, OSError, OverflowError, KeyError):
        # If identification by behavior fails, return empty tuple
        # These exceptions can occur with historical dates or invalid timezone data
        pass

    return ()


def tzid_from_tzinfo(tzinfo: tzinfo | None) -> str | None:
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


def tzid_from_dt(dt: datetime) -> str | None:
    """Retrieve the timezone id from the datetime object."""
    tzid = tzid_from_tzinfo(dt.tzinfo)
    if tzid is None:
        return dt.tzname()
    return tzid


_EQUIVALENT_IDS: dict[str, set[str]] = defaultdict(set)


def _add_equivalent_ids(value: tuple | dict | set):
    """This adds equivalent ids/

    As soon as one timezone implementation used claims their equivalence,
    they are considered equivalent.
    Have a look at icalendar.timezone.equivalent_timezone_ids.
    """
    if isinstance(value, set):
        for tzid in value:
            _EQUIVALENT_IDS[tzid].update(value)
    elif isinstance(value, tuple):
        _add_equivalent_ids(value[1])
    elif isinstance(value, dict):
        for value2 in value.values():
            _add_equivalent_ids(value2)
    else:
        raise TypeError(
            f"Expected tuple, dict or set, not {value.__class__.__name__}: {value!r}"
        )


_add_equivalent_ids(equivalent_timezone_ids_result.lookup)


def get_equivalent_tzids(tzid: str) -> tuple[str]:
    """This returns the tzids which are equivalent to this one."""
    ids = _EQUIVALENT_IDS.get(tzid, set())
    return (tzid,) + tuple(sorted(ids - {tzid}))


def _identify_tzid_by_behavior(
    tzinfo: tzinfo,
    lookup_node: Any,  # Recursive: set[str] | tuple[datetime, dict[timedelta, ...]]
) -> set[str]:
    """Identify timezone by traversing the lookup tree based on utcoffset behavior.

    The lookup tree is structured as:
    - A set of timezone IDs (terminal node)
    - A tuple of (datetime, dict) where:
      - datetime is a transition point
      - dict maps timedelta (utcoffset) to either another tuple or a set

    We use midday (12:00) instead of midnight to avoid timezone transitions,
    as suggested in the issue description.
    """
    if isinstance(lookup_node, set):
        return lookup_node

    if not isinstance(lookup_node, tuple) or len(lookup_node) != 2:
        return set()

    transition_dt, offset_map = lookup_node

    # Use midday (12:00) instead of the transition time to avoid ambiguous
    # timezone definitions around midnight transitions
    # This approach was introduced in issue #776 for generating the lookup tree
    # Make sure the datetime is naive (no tzinfo) as required by utcoffset
    query_dt = transition_dt.replace(hour=12, minute=0, second=0, microsecond=0)
    if query_dt.tzinfo is not None:
        query_dt = query_dt.replace(tzinfo=None)

    try:
        # Get the utcoffset at this point in time
        offset = tzinfo.utcoffset(query_dt)
        if offset is None:
            return set()

        # Find the matching branch in the lookup tree
        if offset in offset_map:
            return _identify_tzid_by_behavior(tzinfo, offset_map[offset])

        # If exact match not found, try to find the closest match
        # This handles cases where the offset might be slightly different
        # due to different timezone database versions
        for candidate_offset, subtree in offset_map.items():
            # Allow small differences (up to 1 hour) to handle DST transitions
            offset_diff = abs((offset - candidate_offset).total_seconds())
            if offset_diff < 3600:  # 1 hour tolerance
                result = _identify_tzid_by_behavior(tzinfo, subtree)
                if result:
                    return result
    except (ValueError, OSError, OverflowError):
        # Handle errors that might occur with historical dates
        # or invalid timezone data
        pass

    return set()


__all__ = ["tzid_from_dt", "tzid_from_tzinfo", "tzids_from_tzinfo"]
