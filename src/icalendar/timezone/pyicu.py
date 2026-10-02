"""Use PyICU timezones."""
from __future__ import annotations
from datetime import datetime, tzinfo
import threading
from typing import TYPE_CHECKING
import icu  # the PyICU module
from .provider import TZProvider

if TYPE_CHECKING:
  from dateutil.rrule import rrule
  from icalendar import prop
  from icalendar.cal import Timezone


class PYICU(TZProvider):
    """Provide icalendar with timezones from pyicu."""
    name = "pyicu"
    _utc: icu.PYICU | None = None
    _init_lock = threading.Lock()

    @property
    def utc(self) -> icu.PYICU:
        """Return the UTC timezone, initializing lazily on first access."""
        if self._utc is None:
            with self._init_lock:
                # Double-check after acquiring lock
                if self._utc is None:
                    PYICU._utc = icu.ICUtzinfo.getInstance("UTC")
        return self._utc  # type: ignore[return-value]

    def localize_utc(self, dt: datetime) -> datetime:
        """Return the datetime in UTC."""
        if getattr(dt, "tzinfo", False) and dt.tzinfo is not None:
            return dt.astimezone(self.utc)
        return self.localize(dt, self.utc)
    
    def localize(self, dt: datetime, tz: tzinfo) -> datetime:
        """Localize a datetime to a timezone."""
        return dt.replace(tzinfo=tz)
    
    def knows_timezone_id(self, tzid: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return tzid in list(icu.TimeZone.createEnumeration())
    
    def timezone(self, name: str) -> tzinfo | None:
        """Return a timezone with a name or None if we cannot find it."""
        if self.knows_timezone_id(name):
            return icu.ICUtzinfo.getInstance(name)
        return None

    def fix_rrule_until(self, rrule: rrule, ical_rrule: prop.vRecur) -> None:
        """Make sure the until value works for the rrule generated from the ical_rrule."""  # noqa: E501
        if not {"UNTIL", "COUNT"}.intersection(ical_rrule.keys()):
            # zoninfo does not know any transition dates after 2038
            rrule._until = datetime(2038, 12, 31, tzinfo=self.utc)  # noqa: SLF001
                
    def create_timezone(self, tz: Timezone) -> tzinfo:
        """Create a timezone from a VTIMEZONE component using PyICU."""
        text = tz.to_ical().decode("UTF-8", "replace")
        vtimezone = icu.VTimeZone.createVTimeZone(text)
        # PyICU does not raise on an unparseable VTIMEZONE — it returns a zone with
        # an empty id whose use segfaults the interpreter. Detect that and fail
        # loudly with a catchable Python error instead.
        tzid = icu.UnicodeString()
        vtimezone.getID(tzid)
        if not str(tzid):
            raise ValueError(f"PyICU could not parse VTIMEZONE {tz.get('TZID')!r}")
        return icu.ICUtzinfo(vtimezone)

    def uses_pytz(self) -> bool:
        """Whether we use pytz."""
        return False
    def uses_zoneinfo(self) -> bool:
        """Whether we use zoneinfo."""
        return False
    def uses_pyicu(self) -> bool:
        """Whether we use pyicu."""
        return True


__all__ = ["PYICU"]