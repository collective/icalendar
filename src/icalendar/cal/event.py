""":rfc:`5545` VEVENT component."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional

from icalendar.attr import (
    X_MOZ_LASTACK_property,
    X_MOZ_SNOOZE_TIME_property,
    categories_property,
    color_property,
    create_single_property,
    description_property,
    exdates_property,
    property_del_duration,
    property_doc_duration_template,
    property_get_duration,
    property_set_duration,
    rdates_property,
    rrules_property,
    sequence_property,
    summary_property,
    uid_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example
from icalendar.error import IncompleteComponent, InvalidCalendar
from icalendar.tools import is_date

if TYPE_CHECKING:
    from icalendar.alarms import Alarms


class Event(Component):
    """
    A "VEVENT" calendar component is a grouping of component
    properties that represents a scheduled amount of time on a
    calendar. For example, it can be an activity, such as a one-hour
    long department meeting from 8:00 AM to 9:00 AM, tomorrow.
    """

    name = "VEVENT"

    canonical_order = (
        "SUMMARY",
        "DTSTART",
        "DTEND",
        "DURATION",
        "DTSTAMP",
        "UID",
        "RECURRENCE-ID",
        "SEQUENCE",
        "RRULE",
        "RDATE",
        "EXDATE",
    )

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CLASS",
        "CREATED",
        "COLOR",
        "DESCRIPTION",
        "DTSTART",
        "GEO",
        "LAST-MODIFIED",
        "LOCATION",
        "ORGANIZER",
        "PRIORITY",
        "DTSTAMP",
        "SEQUENCE",
        "STATUS",
        "SUMMARY",
        "TRANSP",
        "URL",
        "RECURRENCE-ID",
        "DTEND",
        "DURATION",
        "UID",
    )
    exclusive = (
        "DTEND",
        "DURATION",
    )
    multiple = (
        "ATTACH",
        "ATTENDEE",
        "CATEGORIES",
        "COMMENT",
        "CONTACT",
        "EXDATE",
        "RSTATUS",
        "RELATED",
        "RESOURCES",
        "RDATE",
        "RRULE",
    )
    ignore_exceptions = True

    @property
    def alarms(self) -> Alarms:
        """Compute the alarm times for this component.

        >>> from icalendar import Event
        >>> event = Event.example("rfc_9074_example_1")
        >>> len(event.alarms.times)
        1
        >>> alarm_time = event.alarms.times[0]
        >>> alarm_time.trigger  # The time when the alarm pops up
        datetime.datetime(2021, 3, 2, 10, 15, tzinfo=ZoneInfo(key='America/New_York'))
        >>> alarm_time.is_active()  # This alarm has not been acknowledged
        True

        Note that this only uses DTSTART and DTEND, but ignores
        RDATE, EXDATE, and RRULE properties.
        """
        from icalendar.alarms import Alarms

        return Alarms(self)

    @classmethod
    def example(cls, name: str = "rfc_9074_example_3") -> Event:
        """Return the calendar example with the given name."""
        return cls.from_ical(get_example("events", name))

    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VEVENT" specifies the inclusive start of the event.',  # noqa: E501
    )
    DTEND = create_single_property(
        "DTEND",
        "dt",
        (datetime, date),
        date,
        'The "DTEND" property for a "VEVENT" calendar component specifies the non-inclusive end of the event.',  # noqa: E501
    )

    def _get_start_end_duration(self):
        """Verify the calendar validity and return the right attributes."""
        start = self.DTSTART
        end = self.DTEND
        duration = self.DURATION
        if duration is not None and end is not None:
            raise InvalidCalendar(
                "Only one of DTEND and DURATION may be in a VEVENT, not both."
            )
        if (
            isinstance(start, date)
            and not isinstance(start, datetime)
            and duration is not None
            and duration.seconds != 0
        ):
            raise InvalidCalendar(
                "When DTSTART is a date, DURATION must be of days or weeks."
            )
        if start is not None and end is not None and is_date(start) != is_date(end):
            raise InvalidCalendar(
                "DTSTART and DTEND must be of the same type, either date or datetime."
            )
        return start, end, duration

    DURATION = property(
        property_get_duration,
        property_set_duration,
        property_del_duration,
        property_doc_duration_template.format(component="VEVENT"),
    )

    @property
    def duration(self) -> timedelta:
        """The duration of the VEVENT.

        This duration is calculated from the start and end of the event.
        You cannot set the duration as it is unclear what happens to start and end.
        """
        return self.end - self.start

    @property
    def start(self) -> date | datetime:
        """The start of the component.

        Invalid values raise an InvalidCalendar.
        If there is no start, we also raise an IncompleteComponent error.

        You can get the start, end and duration of an event as follows:

        >>> from datetime import datetime
        >>> from icalendar import Event
        >>> event = Event()
        >>> event.start = datetime(2021, 1, 1, 12)
        >>> event.end = datetime(2021, 1, 1, 12, 30) # 30 minutes
        >>> event.duration  # 1800 seconds == 30 minutes
        datetime.timedelta(seconds=1800)
        >>> print(event.to_ical())
        BEGIN:VEVENT
        DTSTART:20210101T120000
        DTEND:20210101T123000
        END:VEVENT
        """
        start = self._get_start_end_duration()[0]
        if start is None:
            raise IncompleteComponent("No DTSTART given.")
        return start

    @start.setter
    def start(self, start: Optional[date | datetime]):
        """Set the start."""
        self.DTSTART = start

    @property
    def end(self) -> date | datetime:
        """The end of the component.

        Invalid values raise an InvalidCalendar error.
        If there is no end, we also raise an IncompleteComponent error.
        """
        start, end, duration = self._get_start_end_duration()
        if end is None and duration is None:
            if start is None:
                raise IncompleteComponent("No DTEND or DURATION+DTSTART given.")
            if is_date(start):
                return start + timedelta(days=1)
            return start
        if duration is not None:
            if start is not None:
                return start + duration
            raise IncompleteComponent("No DTEND or DURATION+DTSTART given.")
        return end

    @end.setter
    def end(self, end: date | datetime | None):
        """Set the end."""
        self.DTEND = end

    X_MOZ_SNOOZE_TIME = X_MOZ_SNOOZE_TIME_property
    X_MOZ_LASTACK = X_MOZ_LASTACK_property
    color = color_property
    sequence = sequence_property
    categories = categories_property
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property
    uid = uid_property
    summary = summary_property
    description = description_property

    @classmethod
    def new(
        cls,
        /,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        dtstamp: Optional[date] = None,
        uid: Optional[str | uuid.UUID] = None,
    ):
        """Create a new event with all required properties.

        This creates a new Event in accordance with :rfc:`5545`.
        """
        event = super().new(dtstamp=dtstamp or cls._utc_now())
        event.summary = summary
        event.description = description
        event.uid = uid or uuid.uuid4()
        return event


__all__ = ["Event"]
