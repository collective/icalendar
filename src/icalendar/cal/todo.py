""":rfc:`5545` VTODO component."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional, Sequence

from icalendar.attr import (
    X_MOZ_LASTACK_property,
    X_MOZ_SNOOZE_TIME_property,
    attendees_property,
    categories_property,
    class_property,
    color_property,
    contacts_property,
    create_single_property,
    description_property,
    exdates_property,
    location_property,
    organizer_property,
    priority_property,
    property_del_duration,
    property_doc_duration_template,
    property_get_duration,
    property_set_duration,
    rdates_property,
    rrules_property,
    sequence_property,
    status_property,
    summary_property,
    uid_property,
    url_property,
)
from icalendar.cal.component import Component
from icalendar.error import IncompleteComponent, InvalidCalendar
from icalendar.tools import is_date

if TYPE_CHECKING:
    from icalendar.alarms import Alarms
    from icalendar.enums import CLASS, STATUS
    from icalendar.prop import vCalAddress


class Todo(Component):
    """
    A "VTODO" calendar component is a grouping of component
    properties that represents an action item or assignment. For
    example, it can be used to represent an item of work assigned to
    an individual, such as "Prepare for the upcoming conference
    seminar on Internet Calendaring".

    Examples:
        Create a new Todo:

            >>> from icalendar import Todo
            >>> todo = Todo.new()
            >>> print(todo.to_ical())
            BEGIN:VTODO
            DTSTAMP:20250517T080612Z
            UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
            END:VTODO

    """

    name = "VTODO"

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CLASS",
        "COLOR",
        "COMPLETED",
        "CREATED",
        "DESCRIPTION",
        "DTSTAMP",
        "DTSTART",
        "GEO",
        "LAST-MODIFIED",
        "LOCATION",
        "ORGANIZER",
        "PERCENT-COMPLETE",
        "PRIORITY",
        "RECURRENCE-ID",
        "SEQUENCE",
        "STATUS",
        "SUMMARY",
        "UID",
        "URL",
        "DUE",
        "DURATION",
    )
    exclusive = (
        "DUE",
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
    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VTODO" specifies the inclusive start of the Todo.',  # noqa: E501
    )
    DUE = create_single_property(
        "DUE",
        "dt",
        (datetime, date),
        date,
        'The "DUE" property for a "VTODO" calendar component specifies the non-inclusive end of the Todo.',  # noqa: E501
    )
    DURATION = property(
        property_get_duration,
        property_set_duration,
        property_del_duration,
        property_doc_duration_template.format(component="VTODO"),
    )

    def _get_start_end_duration(self):
        """Verify the calendar validity and return the right attributes."""
        start = self.DTSTART
        end = self.DUE
        duration = self.DURATION
        if duration is not None and end is not None:
            raise InvalidCalendar(
                "Only one of DUE and DURATION may be in a VTODO, not both."
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
                "DTSTART and DUE must be of the same type, either date or datetime."
            )
        return start, end, duration

    @property
    def start(self) -> date | datetime:
        """The start of the VTODO.

        Invalid values raise an InvalidCalendar.
        If there is no start, we also raise an IncompleteComponent error.

        You can get the start, end and duration of a Todo as follows:

        >>> from datetime import datetime
        >>> from icalendar import Todo
        >>> todo = Todo()
        >>> todo.start = datetime(2021, 1, 1, 12)
        >>> todo.end = datetime(2021, 1, 1, 12, 30) # 30 minutes
        >>> todo.duration  # 1800 seconds == 30 minutes
        datetime.timedelta(seconds=1800)
        >>> print(todo.to_ical())
        BEGIN:VTODO
        DTSTART:20210101T120000
        DUE:20210101T123000
        END:VTODO
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
        """The end of the todo.

        Invalid values raise an InvalidCalendar error.
        If there is no end, we also raise an IncompleteComponent error.
        """
        start, end, duration = self._get_start_end_duration()
        if end is None and duration is None:
            if start is None:
                raise IncompleteComponent("No DUE or DURATION+DTSTART given.")
            if is_date(start):
                return start + timedelta(days=1)
            return start
        if duration is not None:
            if start is not None:
                return start + duration
            raise IncompleteComponent("No DUE or DURATION+DTSTART given.")
        return end

    @end.setter
    def end(self, end: date | datetime | None):
        """Set the end."""
        self.DUE = end

    @property
    def duration(self) -> timedelta:
        """The duration of the VTODO.

        Returns the DURATION property if set, otherwise calculated from start and end.
        For todos, DURATION can exist without DTSTART per RFC 5545.
        """
        # First check if DURATION property is explicitly set
        if "DURATION" in self:
            return self["DURATION"].dt

        # Fall back to calculated duration from start and end
        return self.end - self.start

    X_MOZ_SNOOZE_TIME = X_MOZ_SNOOZE_TIME_property
    X_MOZ_LASTACK = X_MOZ_LASTACK_property

    @property
    def alarms(self) -> Alarms:
        """Compute the alarm times for this component.

        >>> from datetime import datetime
        >>> from icalendar import Todo
        >>> todo = Todo()  # empty without alarms
        >>> todo.start = datetime(2024, 10, 26, 10, 21)
        >>> len(todo.alarms.times)
        0

        Note that this only uses DTSTART and DUE, but ignores
        RDATE, EXDATE, and RRULE properties.
        """
        from icalendar.alarms import Alarms

        return Alarms(self)

    color = color_property
    sequence = sequence_property
    categories = categories_property
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property
    uid = uid_property
    summary = summary_property
    description = description_property
    classification = class_property
    url = url_property
    organizer = organizer_property
    location = location_property
    priority = priority_property
    contacts = contacts_property
    status = status_property
    attendees = attendees_property

    @classmethod
    def new(
        cls,
        /,
        attendees: Optional[list[vCalAddress]] = None,
        categories: Sequence[str] = (),
        classification: Optional[CLASS] = None,
        color: Optional[str] = None,
        comments: list[str] | str | None = None,
        contacts: list[str] | str | None = None,
        created: Optional[date] = None,
        description: Optional[str] = None,
        end: Optional[date | datetime] = None,
        last_modified: Optional[date] = None,
        location: Optional[str] = None,
        organizer: Optional[vCalAddress | str] = None,
        priority: Optional[int] = None,
        sequence: Optional[int] = None,
        stamp: Optional[date] = None,
        start: Optional[date | datetime] = None,
        status: Optional[STATUS] = None,
        summary: Optional[str] = None,
        uid: Optional[str | uuid.UUID] = None,
        url: Optional[str] = None,
    ):
        """Create a new TODO with all required properties.

        This creates a new Todo in accordance with :rfc:`5545`.

        Arguments:
            attendees: The :attr:`attendees` of the todo.
            categories: The :attr:`categories` of the todo.
            classification: The :attr:`classification` of the todo.
            color: The :attr:`color` of the todo.
            comments: The :attr:`Component.comments` of the todo.
            created: The :attr:`Component.created` of the todo.
            description: The :attr:`description` of the todo.
            end: The :attr:`end` of the todo.
            last_modified: The :attr:`Component.last_modified` of the todo.
            location: The :attr:`location` of the todo.
            organizer: The :attr:`organizer` of the todo.
            sequence: The :attr:`sequence` of the todo.
            stamp: The :attr:`Component.DTSTAMP` of the todo.
                If None, this is set to the current time.
            start: The :attr:`start` of the todo.
            status: The :attr:`status` of the todo.
            summary: The :attr:`summary` of the todo.
            uid: The :attr:`uid` of the todo.
                If None, this is set to a new :func:`uuid.uuid4`.
            url: The :attr:`url` of the todo.

        Returns:
            :class:`Todo`

        Raises:
            InvalidCalendar: If the content is not valid according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        todo = super().new(
            stamp=stamp if stamp is not None else cls._utc_now(),
            created=created,
            last_modified=last_modified,
            comments=comments,
        )
        todo.summary = summary
        todo.description = description
        todo.uid = uid if uid is not None else uuid.uuid4()
        todo.start = start
        todo.end = end
        todo.color = color
        todo.categories = categories
        todo.sequence = sequence
        todo.classification = classification
        todo.url = url
        todo.organizer = organizer
        todo.location = location
        todo.priority = priority
        todo.contacts = contacts
        todo.status = status
        todo.attendees = attendees
        if cls._validate_new:
            cls._validate_start_and_end(start, end)
        return todo


__all__ = ["Todo"]
