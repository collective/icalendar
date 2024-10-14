"""Use dateutil timezones."""
from __future__ import annotations
import dateutil
import dateutil.tz
from .. import cal
from datetime import datetime, tzinfo
from typing import Optional
from .provider import TZProvider
from icalendar import prop
from dateutil.rrule import rrule



class DATEUTIL(TZProvider):
    """Provide icalendar with timezones from dateutil."""

    name = "dateutil"

    def localize_utc(self, dt: datetime) -> datetime:
        """Return the datetime in UTC."""
        if getattr(dt, 'tzinfo', False) and dt.tzinfo is not None:
            return dt.astimezone(dateutil.tz.tzutc())
        # assume UTC for naive datetime instances
        dt = dt.replace(tzinfo=dateutil.tz.tzutc())
        return dt

    def localize(self, dt: datetime, tz: tzinfo) -> datetime:
        """Localize a datetime to a timezone."""
        return dt.replace(tzinfo=tz)

    def knows_timezone_id(self, id: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return dateutil.tz.gettz(id) is not None

    def fix_rrule_until(self, rrule:rrule, ical_rrule:prop.vRecur) -> None:
        """Make sure the until value works for the rrule generated from the ical_rrule."""
        if not {'UNTIL', 'COUNT'}.intersection(ical_rrule.keys()):
            # dateutil.timezones don't know any transition dates after 2038
            # either
            rrule._until = datetime(2038, 12, 31, tzinfo=dateutil.tz.UTC)

    def create_timezone(self, tz: cal.Timezone) -> tzinfo:
        """Create a dateutil timezone from the given information."""
        transition_times, transition_info = tz.get_transitions()
        name = tz.tz_name
        cls = type(name, (DstTzInfo,), {
            'zone': name,
            '_utc_transition_times': transition_times,
            '_transition_info': transition_info
        })
        return cls

    def timezone(self, name: str) -> Optional[tzinfo]:
        """Return a timezone with a name or None if we cannot find it."""
        try:
            return dateutil.timezone(name)
        except dateutil.UnknownTimeZoneError:
            pass

    def uses_dateutil(self) -> bool:
        """Whether we use dateutil."""
        return True

    def uses_zoneinfo(self) -> bool:
        """Whether we use zoneinfo."""
        return False


__all__ = ["dateutil"]
