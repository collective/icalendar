"""Errors thrown by icalendar."""


class InvalidCalendar(ValueError):
    """The calendar given is not valid.

    This calendar does not conform with RFC 5545 or breaks other RFCs.
    """


class IncompleteComponent(ValueError):
    """The component is missing attributes.

    The attributes are not required, otherwise this would be
    an InvalidCalendar. But in order to perform calculations,
    this attribute is required.

    This error is not raised in the UPPERCASE properties like .DTSTART,
    only in the lowercase computations like .start.
    """


class IncompleteAlarmInformation(ValueError):
    """The alarms cannot be calculated yet because information is missing."""


class LocalTimezoneMissing(IncompleteAlarmInformation):
    """We are missing the local timezone to compute the value.

    Use Alarms.set_local_timezone().
    """


class ComponentEndMissing(IncompleteAlarmInformation):
    """We are missing the end of a component that the alarm is for.

    Use Alarms.set_end().
    """


class ComponentStartMissing(IncompleteAlarmInformation):
    """We are missing the start of a component that the alarm is for.

    Use Alarms.set_start().
    """


__all__ = [
    "InvalidCalendar",
    "IncompleteComponent",
    "IncompleteAlarmInformation",
    "LocalTimezoneMissing",
    "ComponentEndMissing",
    "ComponentStartMissing",
]
