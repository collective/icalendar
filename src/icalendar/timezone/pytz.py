"""Use pytz timezones."""

from __future__ import annotations

from datetime import datetime, time, tzinfo
from typing import TYPE_CHECKING, overload

import pytz
from pytz.tzinfo import DstTzInfo

from .provider import TZProvider

if TYPE_CHECKING:
    from dateutil.rrule import rrule

    from icalendar import prop
    from icalendar.cal import Timezone


class PYTZ(TZProvider):
    """Provide icalendar with timezones from pytz."""

    name = "pytz"

    def localize_utc(self, dt: datetime) -> datetime:
        """Return the datetime in UTC."""
        if getattr(dt, "tzinfo", False) and dt.tzinfo is not None:
            return dt.astimezone(pytz.utc)
        # assume UTC for naive datetime instances
        return pytz.utc.localize(dt)

    @overload
    def localize(self, dt: datetime, tz: tzinfo) -> datetime: ...

    @overload
    def localize(self, dt: datetime.time, tz: tzinfo) -> datetime.time: ...

    def localize(self, dt: datetime | time, tz: tzinfo) -> datetime | datetime.time:
        """Localize a datetime or a time to a timezone."""
        if isinstance(dt, time):
            dt_full = datetime.combine(datetime(2020, 1, 1), dt)  # noqa: DTZ001
            localized = tz.localize(dt_full)
            return localized.timetz()
        return tz.localize(dt)

    def knows_timezone_id(self, tzid: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return tzid in pytz.all_timezones

    def fix_rrule_until(self, rrule: rrule, ical_rrule: prop.vRecur) -> None:
        """Make sure the until value works for rrules generated from the ical_rrule."""
        if not {"UNTIL", "COUNT"}.intersection(ical_rrule.keys()):
            # pytz.timezones don't know any transition dates after 2038
            # either
            rrule._until = datetime(2038, 12, 31, tzinfo=pytz.UTC)  # noqa: SLF001

    def create_timezone(self, tz: Timezone.Timezone) -> tzinfo:
        """Create a pytz timezone from the given information."""
        transition_times, transition_info = tz.get_transitions()
        name = tz.tz_name
        cls = type(
            name,
            (DstTzInfo,),
            {
                "zone": name,
                "_utc_transition_times": transition_times,
                "_transition_info": transition_info,
            },
        )
        return cls()

    def timezone(self, name: str) -> tzinfo | None:
        """Return a timezone with a name or None if we cannot find it."""
        try:
            return pytz.timezone(name)
        except pytz.UnknownTimeZoneError:
            pass

    def uses_pytz(self) -> bool:
        """Whether we use pytz."""
        return True

    def uses_zoneinfo(self) -> bool:
        """Whether we use zoneinfo."""
        return False


__all__ = ["PYTZ"]
