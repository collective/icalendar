"""Use zoneinfo timezones"""
try:
    import zoneinfo
except:
    from backports import zoneinfo
from datetime import datetime, tzinfo
from typing import Optional


class ZONEINFO:
    """Provide icalendar with timezones from zoneinfo."""

    utc = zoneinfo.ZoneInfo("UTC")

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
        except ValueError:
            pass



__all__ = ["ZONEINFO"]
