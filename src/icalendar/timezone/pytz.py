"""Use pytz timezones."""
import pytz
from .provider import Provider

class PYTZ(Provider):
    """Provide icalendar with timezones from pytz."""

    def make_utc(self, value):
        if getattr(value, 'tzinfo', False) and value.tzinfo is not None:
            return value.astimezone(pytz.utc)
        else:
            # assume UTC for naive datetime instances
            return pytz.utc.localize(value)
