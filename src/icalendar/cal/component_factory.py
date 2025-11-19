"""A factory to create components."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from icalendar.caselessdict import CaselessDict

if TYPE_CHECKING:
    from icalendar import Component


class ComponentFactory(CaselessDict):
    """All components defined in :rfc:`5545` are registered in this factory class.
    To get a component you can use it like this.

    Components for other RFCs are also added if supported.
    If a component class is not supported, yet, it can be created.
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

        self.add_component_class(Calendar)
        self.add_component_class(Event)
        self.add_component_class(Todo)
        self.add_component_class(Journal)
        self.add_component_class(FreeBusy)
        self.add_component_class(Timezone)
        self.add_component_class(TimezoneStandard)
        self.add_component_class(TimezoneDaylight)
        self.add_component_class(Alarm)
        self.add_component_class(Available)
        self.add_component_class(Availability)

    def add_component_class(self, cls: type[Component]) -> None:
        """Add a component class to the factory."""
        self[cls.name] = cls

    def get_component_class(self, name):
        """Get the component class from the factory.

        This also creates the component class if it does not exist.
        """
        component_class = self.get(name)
        if component_class is None:
            from icalendar.cal.component import Component

            component_class = type(
                re.sub(r"[^\w]+", "", name), (Component,), {"name": name.upper()}
            )
            self.add_component_class(component_class)
        return component_class


__all__ = ["ComponentFactory"]
