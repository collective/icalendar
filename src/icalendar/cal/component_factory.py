""""""

from __future__ import annotations

from typing import ClassVar, Optional

from icalendar.caselessdict import CaselessDict


class ComponentFactory(CaselessDict):
    """All components defined in RFC 5545 are registered in this factory class.
    To get a component you can use it like this.
    """

    _instance: ClassVar[Optional[ComponentFactory]] = None

    @classmethod
    def singleton(cls) -> ComponentFactory:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict."""
        super().__init__(*args, **kwargs)
        from icalendar.cal.alarm import Alarm
        from icalendar.cal.calendar import Calendar
        from icalendar.cal.event import Event
        from icalendar.cal.free_busy import FreeBusy
        from icalendar.cal.journal import Journal
        from icalendar.cal.timezone import Timezone, TimezoneDaylight, TimezoneStandard
        from icalendar.cal.todo import Todo

        self["VEVENT"] = Event
        self["VTODO"] = Todo
        self["VJOURNAL"] = Journal
        self["VFREEBUSY"] = FreeBusy
        self["VTIMEZONE"] = Timezone
        self["STANDARD"] = TimezoneStandard
        self["DAYLIGHT"] = TimezoneDaylight
        self["VALARM"] = Alarm
        self["VCALENDAR"] = Calendar


__all__ = ["ComponentFactory"]
