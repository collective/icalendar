from __future__ import annotations
from datetime import datetime
from .cache import _timezone_cache
from .. import cal


class TZP:
    """This is the timezone provider proxy.

    If you would like to have another timezone implementation,
    you can create a new one and pass it to this proxy.
    All of icalendar will then use this timezone implementation.
    """

    def __init__(self):
        """Create a new timezone implementation proxy."""
        self.use_pytz()

    def use_pytz(self):
        """Use pytz as the timezone provider."""
        from .pytz import PYTZ
        self.use(PYTZ())

    def use(self, provider):
        """Use another timezone implementation."""
        self.__provider = provider

    def make_utc(self, value: datetime):
        """Convert a datetime object to use UTC.

        If there is no timezone, UTC is assumed.
        """
        return self.__provider.make_utc(value)

    def cache_timezone_component(self, component: cal.VTIMEZONE):
        """Cache a timezone component."""
        if not self.__provider.knows_timezone_id(component['TZID']) and \
            component['TZID'] not in _timezone_cache:
            _timezone_cache[component['TZID']] = component.to_tz()

    def fix_pytz_rrule_until(self, rrule, component):
        """Make sure the until value works."""
        self.__provider.fix_pytz_rrule_until(rrule, component)

    def create_timezone(self, name: str, transition_times, transition_info):
        """Create a timezone from given information."""
        return self.__provider.create_timezone(name, transition_times, transition_info)





__all__ = ["TZP"]
