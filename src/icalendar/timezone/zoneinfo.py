"""Use zoneinfo timezones"""
from __future__ import annotations
try:
    import zoneinfo
except:
    from backports import zoneinfo
from icalendar import prop
from dateutil.rrule import rrule
from datetime import datetime, tzinfo
from typing import Optional
from .provider import TZProvider


class ZONEINFO(TZProvider):
    """Provide icalendar with timezones from zoneinfo."""

    utc = zoneinfo.ZoneInfo("UTC")
    _available_timezones = zoneinfo.available_timezones()

    def localize(self, dt: datetime, tz: zoneinfo.ZoneInfo) -> datetime:
        """Localize a datetime to a timezone."""
        return dt.replace(tzinfo=tz)

    def localize_utc(self, dt: datetime) -> datetime:
        """Return the datetime in UTC."""
        return self.localize(dt, self.utc)

    def timezone(self, name: str) -> Optional[tzinfo]:
        """Return a timezone with a name or None if we cannot find it."""
        try:
            return zoneinfo.ZoneInfo(name)
        except zoneinfo.ZoneInfoNotFoundError:
            pass

    def knows_timezone_id(self, id: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return id in self._available_timezones

    def fix_rrule_until(self, rrule:rrule, ical_rrule:prop.vRecur) -> None:
        """Make sure the until value works for the rrule generated from the ical_rrule."""
        if not {'UNTIL', 'COUNT'}.intersection(ical_rrule.keys()):
            # zoninfo does not know any transition dates after 2038
            rrule._until = datetime(2038, 12, 31, tzinfo=self.utc)

    def create_timezone(self, name: str, transition_times, transition_info) -> tzinfo:
        """Create a timezone from the given information."""
        cls = type(name, (DstTzInfo,), {
            'zone': name,
            '_utc_transition_times': transition_times,
            '_transition_info': transition_info
        })
        return cls()


__all__ = ["ZONEINFO"]