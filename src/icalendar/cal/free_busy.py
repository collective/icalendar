""""""

from __future__ import annotations

from icalendar.attr import uid_property
from icalendar.cal.component import Component


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


__all__ = ["FreeBusy"]
