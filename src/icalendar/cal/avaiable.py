"""This implements the sub-component "AVAILABLE" of "VAVAILABILITY".

This is specified in :rfc:`7953`.
"""

from .component import Component


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


__all__ = ["Available"]
