""":rfc:`5545` VFREEBUSY component."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from icalendar.attr import (
    CONCEPTS_TYPE_SETTER,
    LINKS_TYPE_SETTER,
    RELATED_TO_TYPE_SETTER,
    REQUEST_STATUS_property,
    contacts_property,
    create_single_property,
    organizer_property,
    uid_property,
    url_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example

if TYPE_CHECKING:
    from icalendar.compatibility import Self
    from icalendar.prop import vCalAddress


class FreeBusy(Component):
    """
        A "VFREEBUSY" calendar component is a grouping of component
        properties that represents either a request for free or busy time
        information, a reply to a request for free or busy time
        information, or a published set of busy time information.

    Examples:
        Create a new FreeBusy:

            >>> from icalendar import FreeBusy
            >>> free_busy = FreeBusy.new()
            >>> print(free_busy.to_ical())
            BEGIN:VFREEBUSY
            DTSTAMP:20250517T080612Z
            UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
            END:VFREEBUSY

        Get the example FreeBusy.

        .. code-block:: pycon

            >>> from icalendar import FreeBusy
            >>> free_busy = FreeBusy.example()
            >>> print(free_busy.to_ical().decode())
            BEGIN:VFREEBUSY
            DTEND:19980410T234500Z
            DTSTAMP:19970901T120000Z
            DTSTART:19980313T141711Z
            FREEBUSY:19980314T233000Z/19980315T003000Z
            FREEBUSY:19980316T153000Z/19980316T163000Z
            FREEBUSY:19980318T030000Z/19980318T040000Z
            ORGANIZER:jsmith@example.com
            UID:19970901T115957Z-76A912@example.com
            URL:http://www.example.com/calendar/busytime/jsmith.ifb
            END:VFREEBUSY

    """

    name = "VFREEBUSY"

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CONTACT",
        "DTSTART",
        "DTEND",
        "DTSTAMP",
        "ORGANIZER",
        "UID",
        "URL",
    )
    multiple = (
        "ATTENDEE",
        "COMMENT",
        "FREEBUSY",
        "REQUEST-STATUS",
    )
    uid = uid_property
    url = url_property
    organizer = organizer_property
    contacts = contacts_property
    REQUEST_STATUS = REQUEST_STATUS_property
    start = DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VFREEBUSY" specifies the inclusive start of the component.',
    )
    end = DTEND = create_single_property(
        "DTEND",
        "dt",
        (datetime, date),
        date,
        'The "DTEND" property for a "VFREEBUSY" calendar component specifies the non-inclusive end of the component.',
    )

    @property
    def duration(self) -> timedelta | None:
        """The duration computed from start and end."""
        if self.DTSTART is None or self.DTEND is None:
            return None
        return self.DTEND - self.DTSTART

    @classmethod
    def new(
        cls,
        /,
        comments: list[str] | str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
        contacts: list[str] | str | None = None,
        end: date | datetime | None = None,
        links: LINKS_TYPE_SETTER = None,
        organizer: vCalAddress | str | None = None,
        refids: list[str] | str | None = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        request_status: list[str] | str | None = None,
        stamp: date | None = None,
        start: date | datetime | None = None,
        uid: str | uuid.UUID | None = None,
        url: str | None = None,
    ) -> Self:
        """Create a new FreeBusy component with all required properties,
        in accordance with :rfc:`5545#section-3.6.4`.

        The FreeBusy component has the required properties of UID and DTSTAMP,
        which may be set with the parameters of ``uid`` and ``stamp``.

        Parameters:
            comments: The :attr:`~icalendar.cal.component.Component.comments` of the component.
            concepts: The :attr:`~icalendar.cal.component.Component.concepts` of the component.
            contacts: The :attr:`contacts` of the component.
            end: The :attr:`end` of the component.
            links: The :attr:`~icalendar.cal.component.Component.links` of the component.
            organizer: The :attr:`organizer` of the component.
            refids: :attr:`~icalendar.cal.component.Component.refids` of the component.
            related_to: :attr:`~icalendar.cal.component.Component.related_to` of the component.
            request_status: The :attr:`REQUEST_STATUS` of the component.
            stamp: The :attr:`~icalendar.cal.component.Component.DTSTAMP` of the component.
                If None, this is set to the current time.
            start: The :attr:`start` of the component.
            uid: The :attr:`uid` of the component.
                If None, this is set to a new :func:`uuid.uuid4`.
            url: The :attr:`url` of the component.

        Returns:
            :class:`FreeBusy`

        Raises:
            :exc:`~icalendar.error.InvalidCalendar`: If the content is not valid
                according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        free_busy: Self = super().new(
            stamp=stamp if stamp is not None else cls._utc_now(),
            comments=comments,
            links=links,
            related_to=related_to,
            refids=refids,
            concepts=concepts,
        )
        free_busy.uid = uid if uid is not None else uuid.uuid4()
        free_busy.url = url
        free_busy.organizer = organizer
        free_busy.contacts = contacts
        free_busy.REQUEST_STATUS = request_status
        free_busy.end = end
        free_busy.start = start

        if cls._validate_new:
            cls._validate_start_and_end(start, end)
        return free_busy

    @classmethod
    def example(cls, name: str = "example") -> FreeBusy:
        """Return the FreeBusy example with the given name."""
        return cls.from_ical(get_example("freebusy", name))


__all__ = ["FreeBusy"]
