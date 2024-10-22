"""Compute the times and states of alarms.

This takes different calendar software into account and RFC 9074 (Alarm Extension).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Optional

from icalendar.cal import Alarm, Component, Event, Todo
from icalendar.prop import vDatetime


class IncompleteAlarmInformation(ValueError):
    """The alarms cannot be calculated yet because information is missing."""


class AlarmTime(ABC):
    """An alarm time with all the information."""

    def __init__(self, alarm: Alarm, trigger : datetime, acknowledged:Optional[datetime], parent: Optional[Component]):
        """Create a new AlarmTime."""
        self._alarm = alarm
        self._parent = parent
        self._trigger = trigger
        self._acknowledged = acknowledged

    @property
    def alarm(self) -> Alarm:
        """The alarm component."""
        return self._alarm

    @property
    def parent(self) -> Optional[Component]:
        """This is the component that contains the alarm.

        This is None if you did not use Alarms.set_component().
        """
        return self._parent

    @property
    def is_active(self) -> bool:
        """Whether this alarm is active (True) or acknowledged (False).

        E.g. in some calendar software, this is True until the user had a look
        at the alarm message and clicked the dismiss button.
        """

    @property
    def trigger(self) -> datetime:
        """This is the time to trigger the alarm."""
        return self._trigger


class Alarms:
    """Compute the times and states of alarms.

    TODO: example!

    RFC 9074 specifies that alarms can also be triggered by proximity.
    This is not implemented yet.
    """

    def __init__(self, component:Optional[Alarm]=None):
        """Start computing alarm times."""
        self._absolute_alarms : list[Alarm] = []

        if isinstance(component, Alarm):
            self.add_alarm(component)

    def from_component(self, component: Event | Todo) -> None:
        """Create an Alarm computation from the component."""

    def set_component(self, component: Component):
        """Optional: Set the component of the computed alarms.

        This does not change the computation in any way.
        It makes it easier to identify the components of the alarms in case
        you combine several computations.
        """

    def add_alarm(self, alarm: Alarm) -> None:
        """Optional: Add an alarm component."""
        trigger = alarm.get("TRIGGER")
        self._absolute_alarms.append(alarm)

    def set_component_start(self, dt: date):
        """Set the start of the component.

        If you have only absolute alarms, this is not required.
        If you have alarms relative to start or end, you need to
        set the start or the end respectively.
        """

    def set_component_end(self, dt: date):
        """Set the end of the component.

        If you have only absolute alarms, this is not required.
        If you have alarms relative to start or end, you need to
        set the start or the end respectively.
        """

    def add_acknowledged_time(self, dt: date) -> None:
        """This is the time when all the alarms of this component were acknowledged.

        You can set several times like this. Only the latest one counts.

        Since RFC 9074 (Alarm Extension) was created later,
        calendar implementations differ in how they ackknowledge alarms.
        E.g. Thunderbird and Google Calendar store the last time
        an event has been acknowledged because of an alarm.
        All alarms that happen before this time will be ackknowledged at
        the same time.
        """

    @property
    def times(self) -> list[AlarmTime]:
        """Compute and return the times of the alarms given.

        If the information for calculation is incomplete, this will raise a
        IncompleteAlarmInformation exception.

        Please make sure to set all the required parameters before calculating.
        If you forget to set the acknowledged times, that is not problem.
        """
        return self._get_absolute_alarm_times()
            
    
    def _get_absolute_alarm_times(self) -> list[AlarmTime]:
        """Return a list of absolute alarm times."""
        result : list[AlarmTime] = []
        for absolute_alarm in self._absolute_alarms:
            trigger : datetime = absolute_alarm["TRIGGER"].dt
            result.append(AlarmTime(absolute_alarm, trigger, None, None))
            repeat = absolute_alarm.REPEAT
            if repeat:
                duration = absolute_alarm.DURATION
                # TODO: test duration should not be None
                for i in range(1, repeat + 1):
                    result.append(AlarmTime(absolute_alarm, trigger + duration * i, None, None))
        return result


__all__ = ["Alarms", "AlarmTime", "IncompleteAlarmInformation"]
