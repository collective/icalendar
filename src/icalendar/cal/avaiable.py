"""This implements the sub-component "AVAILABLE" of "VAVAILABILITY".

This is specified in :rfc:`7953`.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional, Sequence

from icalendar.attr import (
    categories_property,
    description_property,
    location_property,
    sequence_property,
    summary_property,
    uid_property,
)

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
    """

    name = "VAVAILABLE"

    summary = summary_property
    description = description_property
    sequence = sequence_property
    categories = categories_property
    uid = uid_property
    location = location_property

    @classmethod
    def new(
        cls,
        /,
        categories: Sequence[str] = (),
        description: Optional[str] = None,
        dtstamp: Optional[date] = None,
        location: Optional[str] = None,
        sequence: Optional[int] = None,
        summary: Optional[str] = None,
        uid: Optional[str | uuid.UUID] = None,
    ):
        """Create a new Available component with all required properties.

        This creates a new Available component in accordance with :rfc:`5545`.

        Arguments:
            categories: The :attr:`categories` of the Available component.
            description: The :attr:`description` of the Available component.
            dtstamp: The :attr:`DTSTAMP` of the Available component.
                If None, this is set to the current time.
            location: The :attr:`location` of the Available component.
            sequence: The :attr:`sequence` of the Available component.
            summary: The :attr:`summary` of the Available component.
            uid: The :attr:`uid` of the Available component.
                If None, this is set to a new :func:`uuid.uuid4`.

        Returns:
            :class:`Available`

        Raises:
            IncompleteComponent: If the content is not valid according to :rfc:`7953`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        available = super().new(
            dtstamp=dtstamp if dtstamp is not None else cls._utc_now()
        )
        available.summary = summary
        available.description = description
        available.uid = uid if uid is not None else uuid.uuid4()
        available.sequence = sequence
        available.categories = categories
        available.location = location
        return available


__all__ = ["Available"]
