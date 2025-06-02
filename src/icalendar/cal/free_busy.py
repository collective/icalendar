""":rfc:`5545` VFREEBUSY component."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from icalendar.attr import organizer_property, uid_property, url_property
from icalendar.cal.component import Component

if TYPE_CHECKING:
    from datetime import date

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
        "RSTATUS",
    )
    uid = uid_property
    url = url_property
    organizer = organizer_property

    @classmethod
    def new(
        cls,
        /,
        dtstamp: Optional[date] = None,
        organizer: Optional[vCalAddress | str] = None,
        uid: Optional[str | uuid.UUID] = None,
        url: Optional[str] = None,
    ):
        """Create a new alarm with all required properties.

        This creates a new Alarm in accordance with :rfc:`5545`.

        Arguments:
            dtstamp: The :attr:`DTSTAMP` of the component.
                If None, this is set to the current time.
            organizer: The :attr:`organizer` of the component.
            uid: The :attr:`uid` of the component.
                If None, this is set to a new :func:`uuid.uuid4`.
            url: The :attr:`url` of the component.

        Returns:
            :class:`FreeBusy`

        Raises:
            IncompleteComponent: If the content is not valid according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        free_busy = super().new(
            dtstamp=dtstamp if dtstamp is not None else cls._utc_now()
        )
        free_busy.uid = uid if uid is not None else uuid.uuid4()
        free_busy.url = url
        free_busy.organizer = organizer
        return free_busy


__all__ = ["FreeBusy"]
