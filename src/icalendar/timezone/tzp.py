from __future__ import annotations
import datetime
from .. import cal
from typing import Optional, Union
from .windows_to_olson import WINDOWS_TO_OLSON
from .provider import TZProvider
from icalendar import prop
from dateutil.rrule import rrule


DEFAULT_TIMEZONE_PROVIDER = "zoneinfo"


class TZP:
    """This is the timezone provider proxy.

    If you would like to have another timezone implementation,
    you can create a new one and pass it to this proxy.
    All of icalendar will then use this timezone implementation.
    """

    def __init__(self, provider:Union[str, TZProvider]=DEFAULT_TIMEZONE_PROVIDER):
        """Create a new timezone implementation proxy."""
        self.use(provider)

    def use_pytz(self) -> None:
        """Use pytz as the timezone provider."""
        from .pytz import PYTZ
        self._use(PYTZ())

    def use_zoneinfo(self) -> None:
        """Use zoneinfo as the timezone provider."""
        from .zoneinfo import ZONEINFO
        self._use(ZONEINFO())

    def _use(self, provider:TZProvider) -> None:
        """Use a timezone implementation."""
        self.__tz_cache = {}
        self.__provider = provider

    def use(self, provider:Union[str, TZProvider]):
        """Switch to a different timezone provider."""
        if isinstance(provider, str):
            provider = getattr(self, f"use_{provider}", None)
            if provider is None:
                raise ValueError(f"Unknown provider {provider_name}. Use 'pytz' or 'zoneinfo'.")
            provider()
        else:
            self._use(provider)

    def use_default(self):
        """Use the default timezone provider."""
        self.use(DEFAULT_TIMEZONE_PROVIDER)

    def localize_utc(self, dt: datetime.datetime) -> datetime.datetime:
        """Return the datetime in UTC.

        If the datetime has no timezone, set UTC as its timezone.
        """
        return self.__provider.localize_utc(dt)

    def localize(self, dt: datetime.datetime, tz: Union[datetime.tzinfo, str]) -> datetime.datetime:
        """Localize a datetime to a timezone."""
        if isinstance(tz, str):
            tz = self.timezone(tz)
        return self.__provider.localize(dt, tz)

    def cache_timezone_component(self, timezone_component: cal.VTIMEZONE) -> None:
        """Cache the timezone that is created from a timezone component
        if it is not already known.

        This can influence the result from timezone(): Once cached, the
        custom timezone is returned from timezone().
        """
        _unclean_id = timezone_component['TZID']
        id = self.clean_timezone_id(_unclean_id)
        if not self.__provider.knows_timezone_id(id) \
            and not self.__provider.knows_timezone_id(_unclean_id) \
            and id not in self.__tz_cache:
            self.__tz_cache[id] = timezone_component.to_tz(self)

    def fix_rrule_until(self, rrule:rrule, ical_rrule:prop.vRecur) -> None:
        """Make sure the until value works."""
        self.__provider.fix_rrule_until(rrule, ical_rrule)

    def create_timezone(self, timezone_component: cal.Timezone) -> datetime.tzinfo:
        """Create a timezone from a timezone component.

        This component will not be cached.
        """
        return self.__provider.create_timezone(timezone_component)

    def clean_timezone_id(self, tzid: str) -> str:
        """Return a clean version of the timezone id.

        Timezone ids can be a bit unclean, starting with a / for example.
        Internally, we should use this to identify timezones.
        """
        return tzid.strip("/")

    def timezone(self, id: str) -> Optional[datetime.tzinfo]:
        """Return a timezone with an id or None if we cannot find it."""
        _unclean_id = id
        id = self.clean_timezone_id(id)
        tz = self.__provider.timezone(id)
        if tz is not None:
            return tz
        if id in WINDOWS_TO_OLSON:
            tz = self.__provider.timezone(WINDOWS_TO_OLSON[id])
        return tz or self.__provider.timezone(_unclean_id) or self.__tz_cache.get(id)

    def uses_pytz(self) -> bool:
        """Whether we use pytz at all."""
        return self.__provider.uses_pytz()

    def uses_zoneinfo(self) -> bool:
        """Whether we use zoneinfo."""
        return self.__provider.uses_zoneinfo()

    @property
    def name(self) -> str:
        """The name of the timezone component used."""
        return self.__provider.name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.name)})"

__all__ = ["TZP"]
