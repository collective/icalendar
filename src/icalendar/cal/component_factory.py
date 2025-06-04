"""A factory to create components."""

from __future__ import annotations

from icalendar.caselessdict import CaselessDict


class ComponentFactory(CaselessDict):
    """All components defined in :rfc:`5545` are registered in this factory class.
    To get a component you can use it like this.
    """

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict."""
        super().__init__(*args, **kwargs)
        from icalendar.cal.alarm import Alarm
        from icalendar.cal.availability import Availability
        from icalendar.cal.available import Available
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
        self["AVAILABLE"] = Available
        self["VAVAILABILITY"] = Availability


__all__ = ["ComponentFactory"]
