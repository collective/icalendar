from __future__ import annotations
import datetime
from .cache import _timezone_cache
from .. import cal
from typing import Optional
from .windows_to_olson import WINDOWS_TO_OLSON


class TZP:
    """This is the timezone provider proxy.

    If you would like to have another timezone implementation,
    you can create a new one and pass it to this proxy.
    All of icalendar will then use this timezone implementation.
    """

    def __init__(self):
        """Create a new timezone implementation proxy."""
        self.use_pytz()

    def use_pytz(self) -> None:
        """Use pytz as the timezone provider."""
        from .pytz import PYTZ
        self.use(PYTZ())

    def use(self, provider) -> None:
        """Use another timezone implementation."""
        self.__provider = provider

    def localize_utc(self, dt: datetime.datetime)-> datetime.datetime:
        """Return the datetime in UTC.

        If the datetime has no timezone, UTC is set.
        """
        return self.__provider.localize_utc(dt)

    def localize(self, dt: datetime.datetime, tz: datetime.tzinfo) -> datetime.datetime:
        """Localize a datetime to a timezone."""
        return self.__provider.localize(dt, tz)

    def cache_timezone_component(self, component: cal.VTIMEZONE) -> None:
        """Cache a timezone component."""
        if not self.__provider.knows_timezone_id(component['TZID']) and \
            component['TZID'] not in _timezone_cache:
            _timezone_cache[component['TZID']] = component.to_tz()

    def fix_pytz_rrule_until(self, rrule, component) -> None:
        """Make sure the until value works."""
        self.__provider.fix_pytz_rrule_until(rrule, component)

    def create_timezone(self, name: str, transition_times, transition_info) -> datetime.tzinfo:
        """Create a timezone from given information."""
        return self.__provider.create_timezone(name, transition_times, transition_info)

    def timezone(self, id: str) -> datetime.tzinfo:
        """Return a timezone with an id or None if we cannot find it."""
        clean_id = id.strip("/")
        tz = self.__provider.timezone(clean_id)
        if tz is not None:
            return tz
        if clean_id in WINDOWS_TO_OLSON:
            tz = self.__provider.timezone(WINDOWS_TO_OLSON[clean_id])
        return tz or self.__provider.timezone(id) or _timezone_cache.get(id)


__all__ = ["TZP"]
