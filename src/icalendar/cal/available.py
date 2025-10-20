"""This implements the sub-component "AVAILABLE" of "VAVAILABILITY".

This is specified in :rfc:`7953`.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Sequence

from icalendar.attr import (
    categories_property,
    contacts_property,
    description_property,
    duration_property,
    exdates_property,
    location_property,
    rdates_property,
    rfc_7953_dtend_property,
    rfc_7953_dtstart_property,
    rfc_7953_duration_property,
    rfc_7953_end_property,
    rrules_property,
    sequence_property,
    summary_property,
    uid_property,
)
from icalendar.cal.examples import get_example
from icalendar.error import InvalidCalendar

from .component import Component

if TYPE_CHECKING:
    from datetime import date


class Available(Component):
    """Sub-component of "VAVAILABILITY from :rfc:`7953`.

    Description:
        "AVAILABLE" subcomponents are used to indicate periods of free
        time within the time range of the enclosing "VAVAILABILITY"
        component.  "AVAILABLE" subcomponents MAY include recurrence
        properties to specify recurring periods of time, which can be
        overridden using normal iCalendar recurrence behavior (i.e., use
        of the "RECURRENCE-ID" property).

    Examples:
        This is a recurring "AVAILABLE" subcomponent:

        .. code-block:: text

            BEGIN:AVAILABLE
            UID:57DD4AAF-3835-46B5-8A39-B3B253157F01
            SUMMARY:Monday to Friday from 9:00 to 17:00
            DTSTART;TZID=America/Denver:20111023T090000
            DTEND;TZID=America/Denver:20111023T170000
            RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR
            LOCATION:Denver
            END:AVAILABLE

        You can get the same example from :meth:`example`:

        .. code-block: pycon

            >>> from icalendar import Available
            >>> a = Available.example()
            >>> str(a.summary)
            'Monday to Friday from 9:00 to 17:00'

    """

    name = "VAVAILABLE"

    summary = summary_property
    description = description_property
    sequence = sequence_property
    categories = categories_property
    uid = uid_property
    location = location_property
    contacts = contacts_property
    exdates = exdates_property
    rdates = rdates_property
    rrules = rrules_property

    start = DTSTART = rfc_7953_dtstart_property
    DTEND = rfc_7953_dtend_property
    DURATION = duration_property("Available")
    duration = rfc_7953_duration_property
    end = rfc_7953_end_property

    @classmethod
    def new(
        cls,
        /,
        categories: Sequence[str] = (),
        comments: list[str] | str | None = None,
        contacts: list[str] | str | None = None,
        created: Optional[date] = None,
        description: Optional[str] = None,
        end: Optional[datetime] = None,
        last_modified: Optional[date] = None,
        location: Optional[str] = None,
        sequence: Optional[int] = None,
        stamp: Optional[date] = None,
        start: Optional[datetime] = None,
        summary: Optional[str] = None,
        uid: Optional[str | uuid.UUID] = None,
    ):
        """Create a new Available component with all required properties.

        This creates a new Available component in accordance with :rfc:`7953`.

        Arguments:
            categories: The :attr:`categories` of the Available component.
            comments: The :attr:`Component.comments` of the Available component.
            contacts: The :attr:`contacts` of the Available component.
            created: The :attr:`Component.created` of the Available component.
            description: The :attr:`description` of the Available component.
            last_modified: The :attr:`Component.last_modified` of the
                Available component.
            location: The :attr:`location` of the Available component.
            sequence: The :attr:`sequence` of the Available component.
            stamp: The :attr:`Component.stamp` of the Available component.
                If None, this is set to the current time.
            summary: The :attr:`summary` of the Available component.
            uid: The :attr:`uid` of the Available component.
                If None, this is set to a new :func:`uuid.uuid4`.

        Returns:
            :class:`Available`

        Raises:
            InvalidCalendar: If the content is not valid according to :rfc:`7953`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        available = super().new(
            stamp=stamp if stamp is not None else cls._utc_now(),
            created=created,
            last_modified=last_modified,
        )
        available.summary = summary
        available.description = description
        available.uid = uid if uid is not None else uuid.uuid4()
        available.sequence = sequence
        available.categories = categories
        available.location = location
        available.comments = comments
        available.contacts = contacts
        if cls._validate_new:
            if end is not None and (
                not isinstance(end, datetime) or end.tzinfo is None
            ):
                raise InvalidCalendar(
                    "Available end must be a datetime with a timezone"
                )
            if not isinstance(start, datetime) or start.tzinfo is None:
                raise InvalidCalendar(
                    "Available start must be a datetime with a timezone"
                )
            available._validate_start_and_end(start, end)  # noqa: SLF001
        available.start = start
        available.end = end
        return available

    @classmethod
    def example(cls, name: str = "rfc_7953_1") -> Available:
        """Return the calendar example with the given name."""
        return cls.from_ical(get_example("availabilities", name)).available[0]


__all__ = ["Available"]
