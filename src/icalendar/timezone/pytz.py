"""Use pytz timezones."""
from __future__ import annotations
import pytz
from datetime import datetime, tzinfo
from pytz.tzinfo import DstTzInfo
from typing import Optional
from .provider import TZProvider
from icalendar import prop
from dateutil.rrule import rrule



class PYTZ(TZProvider):
    """Provide icalendar with timezones from pytz."""

    def localize_utc(self, dt: datetime) -> datetime:
        """Return the datetime in UTC."""
        if getattr(dt, 'tzinfo', False) and dt.tzinfo is not None:
            return dt.astimezone(pytz.utc)
        else:
            # assume UTC for naive datetime instances
            return pytz.utc.localize(dt)

    def localize(self, dt: datetime, tz: tzinfo) -> datetime:
        """Localize a datetime to a timezone."""
        return tz.localize(dt)

    def knows_timezone_id(self, id: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return id in pytz.all_timezones

    def fix_rrule_until(self, rrule:rrule, ical_rrule:prop.vRecur) -> None:
        """Make sure the until value works for the rrule generated from the ical_rrule."""
        if not {'UNTIL', 'COUNT'}.intersection(ical_rrule.keys()):
            # pytz.timezones don't know any transition dates after 2038
            # either
            rrule._until = datetime(2038, 12, 31, tzinfo=pytz.UTC)

    def create_timezone(self, name: str, transition_times, transition_info) -> tzinfo:
        """Create a pytz timezone from the given information."""
        cls = type(name, (DstTzInfo,), {
            'zone': name,
            '_utc_transition_times': transition_times,
            '_transition_info': transition_info
        })
        return cls()

    def timezone(self, name: str) -> Optional[tzinfo]:
        """Return a timezone with a name or None if we cannot find it."""
        try:
            return pytz.timezone(name)
        except pytz.UnknownTimeZoneError:
            pass


__all__ = ["PYTZ"]
