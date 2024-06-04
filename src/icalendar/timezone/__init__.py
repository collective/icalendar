"""This package contains all functionality for timezones."""
from .tzp import TZP
from datetime import datetime
from typing import Optional

tzp = TZP()
tzp.use_pytz()

def tzid_from_dt(dt: datetime) -> Optional[str]:
    """Retrieve the timezone id from the datetime object."""
    tzid = None
    if hasattr(dt.tzinfo, 'zone'):
        tzid = dt.tzinfo.zone  # pytz implementation
    elif hasattr(dt.tzinfo, 'key'):
        tzid = dt.tzinfo.key  # ZoneInfo implementation
    elif hasattr(dt.tzinfo, 'tzname'):
        # dateutil implementation, but this is broken
        # See https://github.com/collective/icalendar/issues/333 for details
        tzid = dt.tzinfo.tzname(dt)
    return tzid


__all__ = ["tzp", "tzid_from_dt"]
