""":rfc:`5545` VEVENT component."""

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
    transparency_property,
    uid_property,
    url_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example
from icalendar.error import IncompleteComponent, InvalidCalendar
from icalendar.tools import is_date

if TYPE_CHECKING:
    from icalendar.alarms import Alarms
    from icalendar.enums import CLASS, STATUS, TRANSP
    from icalendar.prop import vCalAddress


class Event(Component):
    """A grouping of component properties that describe an event.

    Description:
        A "VEVENT" calendar component is a grouping of
        component properties, possibly including "VALARM" calendar
        components, that represents a scheduled amount of time on a
        calendar.  For example, it can be an activity; such as a one-hour
        long, department meeting from 8:00 AM to 9:00 AM, tomorrow.
        Generally, an event will take up time on an individual calendar.
        Hence, the event will appear as an opaque interval in a search for
        busy time.  Alternately, the event can have its Time Transparency
        set to "TRANSPARENT" in order to prevent blocking of the event in
        searches for busy time.

        The "VEVENT" is also the calendar component used to specify an
        anniversary or daily reminder within a calendar.  These events
        have a DATE value type for the "DTSTART" property instead of the
        default value type of DATE-TIME.  If such a "VEVENT" has a "DTEND"
        property, it MUST be specified as a DATE value also.  The
        anniversary type of "VEVENT" can span more than one date (i.e.,
        "DTEND" property value is set to a calendar date after the
        "DTSTART" property value).  If such a "VEVENT" has a "DURATION"
        property, it MUST be specified as a "dur-day" or "dur-week" value.

        The "DTSTART" property for a "VEVENT" specifies the inclusive
        start of the event.  For recurring events, it also specifies the
        very first instance in the recurrence set.  The "DTEND" property
        for a "VEVENT" calendar component specifies the non-inclusive end
        of the event.  For cases where a "VEVENT" calendar component
        specifies a "DTSTART" property with a DATE value type but no
        "DTEND" nor "DURATION" property, the event's duration is taken to
        be one day.  For cases where a "VEVENT" calendar component
        specifies a "DTSTART" property with a DATE-TIME value type but no
        "DTEND" property, the event ends on the same calendar date and
        time of day specified by the "DTSTART" property.

        The "VEVENT" calendar component cannot be nested within another
        calendar component.  However, "VEVENT" calendar components can be
        related to each other or to a "VTODO" or to a "VJOURNAL" calendar
        component with the "RELATED-TO" property.

    Examples:
        The following is an example of the "VEVENT" calendar
        component used to represent a meeting that will also be opaque to
        searches for busy time:

        .. code-block:: text

            BEGIN:VEVENT
            UID:19970901T130000Z-123401@example.com
            DTSTAMP:19970901T130000Z
            DTSTART:19970903T163000Z
            DTEND:19970903T190000Z
            SUMMARY:Annual Employee Review
            CLASS:PRIVATE
            CATEGORIES:BUSINESS,HUMAN RESOURCES
            END:VEVENT

        The following is an example of the "VEVENT" calendar component
        used to represent a reminder that will not be opaque, but rather
        transparent, to searches for busy time:

        .. code-block:: text

            BEGIN:VEVENT
            UID:19970901T130000Z-123402@example.com
            DTSTAMP:19970901T130000Z
            DTSTART:19970401T163000Z
            DTEND:19970402T010000Z
            SUMMARY:Laurel is in sensitivity awareness class.
            CLASS:PUBLIC
            CATEGORIES:BUSINESS,HUMAN RESOURCES
            TRANSP:TRANSPARENT
            END:VEVENT

        The following is an example of the "VEVENT" calendar component
        used to represent an anniversary that will occur annually:

        .. code-block:: text

            BEGIN:VEVENT
            UID:19970901T130000Z-123403@example.com
            DTSTAMP:19970901T130000Z
            DTSTART;VALUE=DATE:19971102
            SUMMARY:Our Blissful Anniversary
            TRANSP:TRANSPARENT
            CLASS:CONFIDENTIAL
            CATEGORIES:ANNIVERSARY,PERSONAL,SPECIAL OCCASION
            RRULE:FREQ=YEARLY
            END:VEVENT

        The following is an example of the "VEVENT" calendar component
        used to represent a multi-day event scheduled from June 28th, 2007
        to July 8th, 2007 inclusively.  Note that the "DTEND" property is
        set to July 9th, 2007, since the "DTEND" property specifies the
        non-inclusive end of the event.

        .. code-block:: text

            BEGIN:VEVENT
            UID:20070423T123432Z-541111@example.com
            DTSTAMP:20070423T123432Z
            DTSTART;VALUE=DATE:20070628
            DTEND;VALUE=DATE:20070709
            SUMMARY:Festival International de Jazz de Montreal
            TRANSP:TRANSPARENT
            END:VEVENT

        Create a new Event:

        .. code-block:: python

            >>> from icalendar import Event
            >>> from datetime import datetime
            >>> event = Event.new(start=datetime(2021, 1, 1, 12, 30, 0))
            >>> print(event.to_ical())
            BEGIN:VEVENT
            DTSTART:20210101T123000
            DTSTAMP:20250517T080612Z
            UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
            END:VEVENT

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

        Returns the DURATION property if set, otherwise calculated from start and end.
        When setting duration, the end time is automatically calculated from start + duration.
        """
        # First check if DURATION property is explicitly set
        if "DURATION" in self:
            return self["DURATION"].dt

        # Fall back to calculated duration from start and end
        return self.end - self.start

    @duration.setter
    def duration(self, duration: timedelta):
        """Set the duration of the event.

        This automatically calculates and sets the end time as start + duration.
        If no start time is set, raises IncompleteComponent.
        """
        if (
            not hasattr(self, "_get_start_end_duration")
            or self._get_start_end_duration()[0] is None
        ):
            raise IncompleteComponent(
                "Cannot set duration without DTSTART. Set start time first."
            )

        start_time = self.start
        self.end = start_time + duration

    @property
    def start(self) -> date | datetime:
        """The start of the event.

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
        """The end of the event.

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
    classification = class_property
    url = url_property
    organizer = organizer_property
    location = location_property
    priority = priority_property
    contacts = contacts_property
    transparency = transparency_property
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
        transparency: Optional[TRANSP] = None,
        summary: Optional[str] = None,
        uid: Optional[str | uuid.UUID] = None,
        url: Optional[str] = None,
    ):
        """Create a new event with all required properties.

        This creates a new Event in accordance with :rfc:`5545`.

        Arguments:
            attendees: The :attr:`attendees` of the event.
            categories: The :attr:`categories` of the event.
            classification: The :attr:`classification` of the event.
            color: The :attr:`color` of the event.
            comments: The :attr:`Component.comments` of the event.
            created: The :attr:`Component.created` of the event.
            description: The :attr:`description` of the event.
            end: The :attr:`end` of the event.
            last_modified: The :attr:`Component.last_modified` of the event.
            location: The :attr:`location` of the event.
            organizer: The :attr:`organizer` of the event.
            priority: The :attr:`priority` of the event.
            sequence: The :attr:`sequence` of the event.
            stamp: The :attr:`Component.stamp` of the event.
                If None, this is set to the current time.
            start: The :attr:`start` of the event.
            status: The :attr:`status` of the event.
            summary: The :attr:`summary` of the event.
            transparency: The :attr:`transparency` of the event.
            uid: The :attr:`uid` of the event.
                If None, this is set to a new :func:`uuid.uuid4`.
            url: The :attr:`url` of the event.

        Returns:
            :class:`Event`

        Raises:
            InvalidCalendar: If the content is not valid according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        event = super().new(
            stamp=stamp if stamp is not None else cls._utc_now(),
            created=created,
            last_modified=last_modified,
            comments=comments,
        )
        event.summary = summary
        event.description = description
        event.uid = uid if uid is not None else uuid.uuid4()
        event.start = start
        event.end = end
        event.color = color
        event.categories = categories
        event.sequence = sequence
        event.classification = classification
        event.url = url
        event.organizer = organizer
        event.location = location
        event.priority = priority
        event.transparency = transparency
        event.contacts = contacts
        event.status = status
        event.attendees = attendees
        if cls._validate_new:
            cls._validate_start_and_end(start, end)
        return event


__all__ = ["Event"]
