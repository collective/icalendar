from __future__ import absolute_import

SEQUENCE_TYPES = (list, tuple)
DEFAULT_ENCODING = 'utf-8'


def to_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even if it is already a unicode string.
    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, str):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            return value.decode('utf-8', 'replace')
    raise AssertionError('A str/unicode expected.')


from .cal import (
    Calendar,
    Event,
    Todo,
    Journal,
    Timezone,
    TimezoneStandard,
    TimezoneDaylight,
    FreeBusy,
    Alarm,
    ComponentFactory,
)
# Property Data Value Types
from .prop import (
    vBinary,
    vBoolean,
    vCalAddress,
    vDatetime,
    vDate,
    vDDDTypes,
    vDuration,
    vFloat,
    vInt,
    vPeriod,
    vWeekday,
    vFrequency,
    vRecur,
    vText,
    vTime,
    vUri,
    vGeo,
    vUTCOffset,
    TypesFactory,
)
# useful tzinfo subclasses
from .prop import (
    FixedOffset,
    LocalTimezone,
)
# Parameters and helper methods for splitting and joining string with escaped
# chars.
from .parser import (
    Parameters,
    q_split,
    q_join,
)


__all__ = [
    Calendar, Event, Todo, Journal,
    FreeBusy, Alarm, ComponentFactory,
    Timezone, TimezoneStandard, TimezoneDaylight,
    vBinary, vBoolean, vCalAddress, vDatetime, vDate,
    vDDDTypes, vDuration, vFloat, vInt, vPeriod,
    vWeekday, vFrequency, vRecur, vText, vTime, vUri,
    vGeo, vUTCOffset, TypesFactory,
    FixedOffset, LocalTimezone,
    Parameters, q_split, q_join,
]
