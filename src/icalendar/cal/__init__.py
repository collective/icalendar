"""Calendar is a dictionary like Python object that can render itself as VCAL
files according to RFC 5545.

These are the defined components.
"""

from icalendar.error import IncompleteComponent

from .alarm import Alarm
from .calendar import Calendar
from .component import Component
from .event import Event
from .examples import get_example
from .free_busy import FreeBusy
from .journal import Journal
from .timezone import Timezone, TimezoneDaylight, TimezoneStandard
from .todo import Todo

__all__ = [
    "Alarm",
    "Calendar",
    "Component",
    "Event",
    "FreeBusy",
    "IncompleteComponent",
    "Journal",
    "Timezone",
    "TimezoneDaylight",
    "TimezoneStandard",
    "Todo",
    "get_example",
]
