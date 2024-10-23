"""Compute the times and states of alarms.

This takes different calendar software into account and RFC 9074 (Alarm Extension).

- Outlook does not export VALARM information
- Google Calendar uses the DTSTAMP to acknowledge the alarms
- Thunderbird snoozes the alarms with a X-MOZ-SNOOZE-TIME attribute in the event
- Thunderbird acknowledges the alarms with a X-MOZ-LASTACK attribute in the event
- Etar deletes alarms that are not active any more
"""

from __future__ import annotations

from datetime import date, timedelta, tzinfo
from typing import TYPE_CHECKING, Generator, Optional, Union

from icalendar.cal import Alarm, Event, Todo
from icalendar.timezone import tzp
from icalendar.tools import is_date, normalize_pytz, to_datetime

if TYPE_CHECKING:
    from datetime import datetime

Parent = Union[Event,Todo]


class IncompleteAlarmInformation(ValueError):
    """The alarms cannot be calculated yet because information is missing."""


class AlarmTime:
    """An alarm time with all the information."""

    def __init__(
            self,
            alarm: Alarm,
            trigger : datetime,
            acknowledged_until:Optional[datetime]=None,
            snoozed_until:Optional[datetime]=None,
            parent: Optional[Parent]=None
        ):
        """Create a new AlarmTime.
        
        alarm - the Alarm component
        trigger - a date or datetime at which to trigger the alarm
        acknowledged_until - an optional datetime in UTC until when all alarms
            have been acknowledged
        snoozed_until - an optional datetime in UTC until which all alarms of
            the same parent are snoozed
        parent - the optional parent component the alarm refers to
        """
        self._alarm = alarm
        self._parent = parent
        self._trigger = trigger
        self._last_ack = acknowledged_until
        self._snooze_until = snoozed_until

    @property
    def alarm(self) -> Alarm:
        """The alarm component."""
        return self._alarm

    @property
    def parent(self) -> Optional[Parent]:
        """This is the component that contains the alarm.

        This is None if you did not use Alarms.set_component().
        """
        return self._parent

    def is_active_in(self, timezone:Optional[tzinfo]=None) -> bool:
        """Whether this alarm is active (True) or acknowledged (False).

        E.g. in some calendar software, this is True until the user had a look
        at the alarm message and clicked the dismiss button.

        Alarms can be in local time (without a timezone).
        To calculate if the alarm really happened, we need it to be in a timezone.
        If a timezone is required but not given, we throw an IncompleteAlarmInformation.
        """
        if not self._last_ack:
            # if nothing is acknowledged, this alarm counts
            return True
        trigger = self.trigger if timezone is None else tzp.localize(self.trigger, timezone)
        if trigger.tzinfo is None:
            raise IncompleteAlarmInformation("A timezone is required to check if the alarm is still active.")
        if self._snooze_until is not None and self._snooze_until > self._last_ack:
            return True
        # print(f"trigger == {trigger} > {self._last_ack} == last ack")
        return trigger > self._last_ack

    @property
    def trigger(self) -> date:
        """This is the time to trigger the alarm.

        If the alarm has been snoozed, this can differ from the TRIGGER property.
        Use is_active_in() to avoid timezone issues.
        """
        return self._trigger


class Alarms:
    """Compute the times and states of alarms.

    TODO: example!

    RFC 9074 specifies that alarms can also be triggered by proximity.
    This is not implemented yet.
    """

    def __init__(self, component:Optional[Alarm|Event|Todo]=None):
        """Start computing alarm times."""
        self._absolute_alarms : list[Alarm] = []
        self._start_alarms : list[Alarm] = []
        self._end_alarms : list[Alarm] = []
        self._start : Optional[date] = None
        self._end : Optional[date] = None
        self._parent : Optional[Parent] = None
        self._last_ack : Optional[datetime] = None
        self._snooze_until : Optional[datetime] = None

        if component is not None:
            self.add_component(component)

    def add_component(self, component:Alarm|Parent):
        """Add a component.

        If this is an alarm, it is added.
        Events and Todos are added as a parent and all
        their alarms are added, too.
        """
        if isinstance(component, (Event, Todo)):
            self.set_parent(component)
            self.set_start(component.start)
            self.set_end(component.end)
            if component.is_thunderbird():
                self.acknowledge_until(component.X_MOZ_LASTACK)
                self.snooze_until(component.X_MOZ_SNOOZE_TIME)
            else:
                self.acknowledge_until(component.DTSTAMP)

        for alarm in component.walk("VALARM"):
            self.add_alarm(alarm)

    def set_parent(self, parent: Parent):
        """Set the parent of all the alarms.

        If you would like to collect alarms from a component, use add_component
        """
        if self._parent is not None and self._parent is not parent:
            raise ValueError("You can only set one parent for this alarm calculation.")
        self._parent = parent

    def add_alarm(self, alarm: Alarm) -> None:
        """Optional: Add an alarm component."""
        trigger = alarm.get("TRIGGER")
        if trigger is None:
            return
        if isinstance(trigger.dt, date):
            self._absolute_alarms.append(alarm)
        elif trigger.params.get("RELATED", "START").upper() == "START":
            self._start_alarms.append(alarm)
        else:
            self._end_alarms.append(alarm)

    def set_start(self, dt: date):
        """Set the start of the component.

        If you have only absolute alarms, this is not required.
        If you have alarms relative to the start of a compoment, set the start here.
        """
        self._start = dt

    def set_end(self, dt: date):
        """Set the end of the component.

        If you have only absolute alarms, this is not required.
        If you have alarms relative to the end of a compoment, set the end here.
        """
        self._end = dt

    def _add(self, dt: date, td:timedelta):
        """Add a timedelta to a datetime."""
        if is_date(dt):
            if td.seconds == 0:
                return dt + td
            dt = to_datetime(dt)
        return normalize_pytz(dt + td)

    def acknowledge_until(self, dt: Optional[date]) -> None:
        """This is the time when all the alarms of this component were acknowledged.

        You can set several times like this. Only the last one counts.

        Since RFC 9074 (Alarm Extension) was created later,
        calendar implementations differ in how they acknowledge alarms.
        E.g. Thunderbird and Google Calendar store the last time
        an event has been acknowledged because of an alarm.
        All alarms that happen before this time will be ackknowledged at this dt.
        """
        if dt is not None:
            self._last_ack = tzp.localize_utc(dt)

    def snooze_until(self, dt: Optional[date]) -> None:
        """This is the time when all the alarms of this component were snoozed.

        You can set several times like this. Only the last one counts.
        The alarms are supposed to turn up again at dt when they are not acknowledged
        but snoozed.
        """
        if dt is not None:
            self._snooze_until = tzp.localize_utc(dt)

    @property
    def times(self) -> list[AlarmTime]:
        """Compute and return the times of the alarms given.

        If the information for calculation is incomplete, this will raise a
        IncompleteAlarmInformation exception.

        Please make sure to set all the required parameters before calculating.
        If you forget to set the acknowledged times, that is not problem.
        """
        return (
            self._get_end_alarm_times() +
            self._get_start_alarm_times() +
            self._get_absolute_alarm_times()
        )

    def _repeat(self, first: datetime, alarm: Alarm) -> Generator[datetime]:
        """The times when the alarm is triggered relative to start."""
        yield first # we trigger at the start
        repeat = alarm.REPEAT
        if repeat:
            duration = alarm.DURATION
            for i in range(1, repeat + 1):
                yield self._add(first, duration * i)

    def _alarm_time(self, alarm: Alarm, trigger:date):
        """Create an alarm time with the additional attributes."""
        return AlarmTime(alarm, trigger, self._last_ack, self._snooze_until, self._parent)

    def _get_absolute_alarm_times(self) -> list[AlarmTime]:
        """Return a list of absolute alarm times."""
        return [
            self._alarm_time(alarm , trigger)
            for alarm in self._absolute_alarms
            for trigger in self._repeat(alarm["TRIGGER"].dt, alarm)
        ]

    def _get_start_alarm_times(self) -> list[AlarmTime]:
        """Return a list of alarm times relative to the start of the component."""
        if self._start is None and self._start_alarms:
            raise IncompleteAlarmInformation("Use Alarms.set_start because at least one alarm is relative to the start of a component.")
        return [
            self._alarm_time(alarm , trigger)
            for alarm in self._start_alarms
            for trigger in self._repeat(self._add(self._start, alarm["TRIGGER"].dt), alarm)
        ]

    def _get_end_alarm_times(self) -> list[AlarmTime]:
        """Return a list of alarm times relative to the start of the component."""
        if self._end is None and self._end_alarms:
            raise IncompleteAlarmInformation("Use Alarms.set_end because at least one alarm is relative to the end of a component.")
        return [
            self._alarm_time(alarm , trigger)
            for alarm in self._end_alarms
            for trigger in self._repeat(self._add(self._end, alarm["TRIGGER"].dt), alarm)
        ]

    def active_in(self, timezone:Optional[tzinfo|str]=None) -> list[AlarmTime]:
        """The alarm times that are still active and not acknowledged.

        This considers snoozed alarms.

        Alarms can be in local time (without a timezone).
        To calculate if the alarm really happened, we need it to be in a timezone.
        If a timezone is required but not given, we throw an IncompleteAlarmInformation.
        """
        timezone = tzp.timezone(timezone) if isinstance(timezone, str) else timezone
        return [alarm_time for alarm_time in self.times if alarm_time.is_active_in(timezone)]

__all__ = ["Alarms", "AlarmTime", "IncompleteAlarmInformation"]
