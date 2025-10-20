""":rfc:`5545` VJOURNAL component."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional, Sequence

from icalendar.attr import (
    attendees_property,
    categories_property,
    class_property,
    color_property,
    contacts_property,
    create_single_property,
    descriptions_property,
    exdates_property,
    images_property,
    organizer_property,
    rdates_property,
    rrules_property,
    sequence_property,
    status_property,
    summary_property,
    uid_property,
    url_property,
)
from icalendar.cal.component import Component
from icalendar.error import IncompleteComponent

if TYPE_CHECKING:
    from icalendar.enums import CLASS, STATUS
    from icalendar.prop import vCalAddress


class Journal(Component):
    """A descriptive text at a certain time or associated with a component.

        Description:
            A "VJOURNAL" calendar component is a grouping of
            component properties that represent one or more descriptive text
            notes associated with a particular calendar date.  The "DTSTART"
            property is used to specify the calendar date with which the
            journal entry is associated.  Generally, it will have a DATE value
            data type, but it can also be used to specify a DATE-TIME value
            data type.  Examples of a journal entry include a daily record of
            a legislative body or a journal entry of individual telephone
            contacts for the day or an ordered list of accomplishments for the
            day.

    Examples:
        Create a new Journal:

            >>> from icalendar import Journal
            >>> journal = Journal.new()
            >>> print(journal.to_ical())
            BEGIN:VJOURNAL
            DTSTAMP:20250517T080612Z
            UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
            END:VJOURNAL

    """

    name = "VJOURNAL"

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CLASS",
        "COLOR",
        "CREATED",
        "DTSTART",
        "DTSTAMP",
        "LAST-MODIFIED",
        "ORGANIZER",
        "RECURRENCE-ID",
        "SEQUENCE",
        "STATUS",
        "SUMMARY",
        "UID",
        "URL",
    )
    multiple = (
        "ATTACH",
        "ATTENDEE",
        "CATEGORIES",
        "COMMENT",
        "CONTACT",
        "EXDATE",
        "RELATED",
        "RDATE",
        "RRULE",
        "RSTATUS",
        "DESCRIPTION",
    )

    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VJOURNAL" that specifies the exact date at which the journal entry was made.',  # noqa: E501
    )

    @property
    def start(self) -> date:
        """The start of the Journal.

        The "DTSTART"
        property is used to specify the calendar date with which the
        journal entry is associated.
        """
        start = self.DTSTART
        if start is None:
            raise IncompleteComponent("No DTSTART given.")
        return start

    @start.setter
    def start(self, value: datetime | date) -> None:
        """Set the start of the journal."""
        self.DTSTART = value

    end = start

    @property
    def duration(self) -> timedelta:
        """The journal has no duration: timedelta(0)."""
        return timedelta(0)

    color = color_property
    sequence = sequence_property
    categories = categories_property
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property
    uid = uid_property

    summary = summary_property
    descriptions = descriptions_property
    classification = class_property
    url = url_property
    organizer = organizer_property
    contacts = contacts_property
    status = status_property
    attendees = attendees_property

    @property
    def description(self) -> str:
        """The concatenated descriptions of the journal.

        A Journal can have several descriptions.
        This is a compatibility method.
        """
        descriptions = self.descriptions
        if not descriptions:
            return None
        return "\r\n\r\n".join(descriptions)

    @description.setter
    def description(self, description: Optional[str]):
        """Set the description"""
        self.descriptions = description

    @description.deleter
    def description(self):
        """Delete all descriptions."""
        del self.descriptions

    images = images_property

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
        description: Optional[str | Sequence[str]] = None,
        last_modified: Optional[date] = None,
        organizer: Optional[vCalAddress | str] = None,
        sequence: Optional[int] = None,
        stamp: Optional[date] = None,
        start: Optional[date | datetime] = None,
        status: Optional[STATUS] = None,
        summary: Optional[str] = None,
        uid: Optional[str | uuid.UUID] = None,
        url: Optional[str] = None,
    ):
        """Create a new journal entry with all required properties.

        This creates a new Journal in accordance with :rfc:`5545`.

        Arguments:
            attendees: The :attr:`attendees` of the journal.
            categories: The :attr:`categories` of the journal.
            classification: The :attr:`classification` of the journal.
            color: The :attr:`color` of the journal.
            comments: The :attr:`Component.comments` of the journal.
            created: The :attr:`Component.created` of the journal.
            description: The :attr:`description` of the journal.
            end: The :attr:`end` of the journal.
            last_modified: The :attr:`Component.last_modified` of the journal.
            organizer: The :attr:`organizer` of the journal.
            sequence: The :attr:`sequence` of the journal.
            stamp: The :attr:`Component.stamp` of the journal.
                If None, this is set to the current time.
            start: The :attr:`start` of the journal.
            status: The :attr:`status` of the journal.
            summary: The :attr:`summary` of the journal.
            uid: The :attr:`uid` of the journal.
                If None, this is set to a new :func:`uuid.uuid4`.
            url: The :attr:`url` of the journal.

        Returns:
            :class:`Journal`

        Raises:
            InvalidCalendar: If the content is not valid according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        journal = super().new(
            stamp=stamp if stamp is not None else cls._utc_now(),
            created=created,
            last_modified=last_modified,
            comments=comments,
        )
        journal.summary = summary
        journal.descriptions = description
        journal.uid = uid if uid is not None else uuid.uuid4()
        journal.start = start
        journal.color = color
        journal.categories = categories
        journal.sequence = sequence
        journal.classification = classification
        journal.url = url
        journal.organizer = organizer
        journal.contacts = contacts
        journal.start = start
        journal.status = status
        journal.attendees = attendees
        return journal


__all__ = ["Journal"]
