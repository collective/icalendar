"""Calendar is a dictionary like Python object that can render itself as VCAL
files according to RFC 5545.

These are the defined components.
"""

from icalendar.attr import single_utc_property

from .alarm import Alarm
from .availability import Availability
from .available import Available
from .calendar import Calendar
from .component import Component
from .component_factory import ComponentFactory
from .event import Event
from .free_busy import FreeBusy
from .journal import Journal
from .lazy import LazyCalendar
from .timezone import Timezone, TimezoneDaylight, TimezoneStandard
from .todo import Todo

Todo.COMPLETED = single_utc_property(
    "COMPLETED",
    """The UTC datetime when this to-do was completed.

    This property is defined in :rfc:`5545#section-3.8.2.1`. It appears
    only on ``VTODO`` components. The RFC value type is ``DATE-TIME`` in UTC.

    Date-only values (including ``COMPLETED;VALUE=DATE``) are converted to
    midnight UTC, matching :attr:`~icalendar.Component.DTSTAMP`.
    """,
)

__all__ = [
    "Alarm",
    "Availability",
    "Available",
    "Calendar",
    "Component",
    "ComponentFactory",
    "Event",
    "FreeBusy",
    "Journal",
    "LazyCalendar",
    "Timezone",
    "TimezoneDaylight",
    "TimezoneStandard",
    "Todo",
]
