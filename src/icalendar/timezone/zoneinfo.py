"""Use zoneinfo timezones"""

from __future__ import annotations

from icalendar.tools import is_date, to_datetime

try:
    import zoneinfo
except ImportError:
    from backports import zoneinfo  # type: ignore  # noqa: PGH003
import copy
import copyreg
import functools
from datetime import datetime, tzinfo
from io import StringIO
from typing import TYPE_CHECKING, Optional

from dateutil.rrule import rrule, rruleset
from dateutil.tz import tzical
from dateutil.tz.tz import _tzicalvtz

from .provider import TZProvider

if TYPE_CHECKING:
    from icalendar import cal, prop
    from icalendar.prop import vDDDTypes


class ZONEINFO(TZProvider):
    """Provide icalendar with timezones from zoneinfo."""

    name = "zoneinfo"
    utc = zoneinfo.ZoneInfo("UTC")
    _available_timezones = zoneinfo.available_timezones()

    def localize(self, dt: datetime, tz: zoneinfo.ZoneInfo) -> datetime:
        """Localize a datetime to a timezone."""
        return dt.replace(tzinfo=tz)

    def localize_utc(self, dt: datetime) -> datetime:
        """Return the datetime in UTC."""
        if getattr(dt, "tzinfo", False) and dt.tzinfo is not None:
            return dt.astimezone(self.utc)
        return self.localize(dt, self.utc)

    def timezone(self, name: str) -> Optional[tzinfo]:
        """Return a timezone with a name or None if we cannot find it."""
        try:
            return zoneinfo.ZoneInfo(name)
        except zoneinfo.ZoneInfoNotFoundError:
            pass
        except ValueError:
            # ValueError: ZoneInfo keys may not be absolute paths, got: /Europe/CUSTOM
            pass

    def knows_timezone_id(self, id: str) -> bool:
        """Whether the timezone is already cached by the implementation."""
        return id in self._available_timezones

    def fix_rrule_until(self, rrule: rrule, ical_rrule: prop.vRecur) -> None:
        """Make sure the until value works for the rrule generated from the ical_rrule."""
        if not {"UNTIL", "COUNT"}.intersection(ical_rrule.keys()):
            # zoninfo does not know any transition dates after 2038
            rrule._until = datetime(2038, 12, 31, tzinfo=self.utc)

    def create_timezone(self, tz: cal.Timezone) -> tzinfo:
        """Create a timezone from the given information."""
        try:
            return self._create_timezone(tz)
        except ValueError:
            # We might have a custom component in there.
            # see https://github.com/python/cpython/issues/120217
            tz = copy.deepcopy(tz)
            for sub in tz.walk():
                for attr in list(sub.keys()):
                    if attr.lower().startswith("x-"):
                        sub.pop(attr)
            for sub in tz.subcomponents:
                start : vDDDTypes = sub.get("DTSTART")
                if start and is_date(start.dt):
                    # ValueError: Unsupported DTSTART param in VTIMEZONE: VALUE=DATE
                    sub.DTSTART = to_datetime(start.dt)
            return self._create_timezone(tz)

    def _create_timezone(self, tz: cal.Timezone) -> tzinfo:
        """Create a timezone and maybe fail"""
        file = StringIO(tz.to_ical().decode("UTF-8", "replace"))
        return tzical(file).get()

    def uses_pytz(self) -> bool:
        """Whether we use pytz."""
        return False

    def uses_zoneinfo(self) -> bool:
        """Whether we use zoneinfo."""
        return True


def pickle_tzicalvtz(tzicalvtz: tz._tzicalvtz):
    """Because we use dateutil.tzical, we need to make it pickle-able."""
    return _tzicalvtz, (tzicalvtz._tzid, tzicalvtz._comps)


copyreg.pickle(_tzicalvtz, pickle_tzicalvtz)


def pickle_rrule_with_cache(self: rrule):
    """Make sure we can also pickle rrules that cache.

    This is mainly copied from rrule.replace.
    """
    new_kwargs = {
        "interval": self._interval,
        "count": self._count,
        "dtstart": self._dtstart,
        "freq": self._freq,
        "until": self._until,
        "wkst": self._wkst,
        "cache": False if self._cache is None else True,
    }
    new_kwargs.update(self._original_rule)
    # from https://stackoverflow.com/a/64915638/1320237
    return functools.partial(rrule, new_kwargs.pop("freq"), **new_kwargs), ()


copyreg.pickle(rrule, pickle_rrule_with_cache)


def pickle_rruleset_with_cache(rs: rruleset):
    """Pickle an rruleset."""
    # self._rrule = []
    # self._rdate = []
    # self._exrule = []
    # self._exdate = []
    return unpickle_rruleset_with_cache, (
        rs._rrule,
        rs._rdate,
        rs._exrule,
        rs._exdate,
        False if rs._cache is None else True,
    )


def unpickle_rruleset_with_cache(rrule, rdate, exrule, exdate, cache):
    """unpickling the rruleset."""
    rs = rruleset(cache)
    for o in rrule:
        rs.rrule(o)
    for o in rdate:
        rs.rdate(o)
    for o in exrule:
        rs.exrule(o)
    for o in exdate:
        rs.exdate(o)
    return rs


copyreg.pickle(rruleset, pickle_rruleset_with_cache)

__all__ = ["ZONEINFO"]
