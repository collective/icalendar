"""Use pytz timezones."""
import pytz

class PYTZ:
    """Provide icalendar with timezones from pytz."""

    def make_utc(self, value):
        """See icalendar.timezone.tzp.make_utc."""
        if getattr(value, 'tzinfo', False) and value.tzinfo is not None:
            return value.astimezone(pytz.utc)
        else:
            # assume UTC for naive datetime instances
            return pytz.utc.localize(value)

    def knows_timezone_id(self, id: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return id in pytz.all_timezones
