""":rfc:`5545` VFREEBUSY component."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from icalendar.attr import uid_property
from icalendar.cal.component import Component

if TYPE_CHECKING:
    from datetime import date


class FreeBusy(Component):
    """
    A "VFREEBUSY" calendar component is a grouping of component
    properties that represents either a request for free or busy time
    information, a reply to a request for free or busy time
    information, or a published set of busy time information.
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

    @classmethod
    def new(
        cls,
        /,
        dtstamp: Optional[date] = None,
        uid: Optional[str | uuid.UUID] = None,
    ):
        """Create a new alarm with all required properties.

        This creates a new Alarm in accordance with :rfc:`5545`.
        """
        free_busy = super().new(dtstamp=dtstamp or cls._utc_now())
        free_busy.uid = uid or uuid.uuid4()
        return free_busy


__all__ = ["FreeBusy"]
