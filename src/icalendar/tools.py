from __future__ import annotations
import random
from datetime import date, datetime, tzinfo
from string import ascii_letters, digits

from icalendar.parser_tools import to_unicode


class UIDGenerator:
    """If you are too lazy to create real uid's.

    """
    chars = list(ascii_letters + digits)

    @staticmethod
    def rnd_string(length=16):
        """Generates a string with random characters of length.
        """
        return "".join([random.choice(UIDGenerator.chars) for _ in range(length)])

    @staticmethod
    def uid(host_name="example.com", unique=""):
        """Generates a unique id consisting of:
            datetime-uniquevalue@host.
        Like:
            20050105T225746Z-HKtJMqUgdO0jDUwm@example.com
        """
        from icalendar.prop import vDatetime, vText
        host_name = to_unicode(host_name)
        unique = unique or UIDGenerator.rnd_string()
        today = to_unicode(vDatetime(datetime.today()).to_ical())
        return vText(f"{today}-{unique}@{host_name}")


def is_date(dt: date) -> bool:
    """Whether this is a date and not a datetime."""
    return isinstance(dt, date) and not isinstance(dt, datetime)


def is_datetime(dt: date) -> bool:
    """Whether this is a date and not a datetime."""
    return isinstance(dt, datetime)


def to_datetime(dt: date) -> datetime:
    """Make sure we have a datetime, not a date."""
    if is_date(dt):
        return datetime(dt.year, dt.month, dt.day)  # noqa: DTZ001
    return dt


def is_pytz(tz: tzinfo):
    """Whether the timezone requires localize() and normalize()."""
    return hasattr(tz, "localize")


def is_pytz_dt(dt: date):
    """Whether the time requires localize() and normalize()."""
    return is_datetime(dt) and is_pytz(dt.tzinfo)


def normalize_pytz(dt: date):
    """We have to normalize the time after a calculation if we use pytz.

    pytz requires this function to be used in order to correctly calculate the
    timezone's offset after calculations.
    """
    if is_pytz_dt(dt):
        return dt.tzinfo.normalize(dt)
    return dt


__all__ = ["UIDGenerator", "is_date", "is_datetime", "to_datetime", "is_pytz", "is_pytz_dt", "normalize_pytz"]
