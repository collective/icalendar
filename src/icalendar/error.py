"""Errors thrown by icalendar."""

from __future__ import annotations

import contextlib


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


class FeatureWillBeRemovedInFutureVersion(DeprecationWarning):
    """This feature will be removed in a future version."""


class JCalParsingError(ValueError):
    """Could not parse a part of the JCal."""

    def __init__(
        self,
        message: str,
        parser: str | type = "",
        path: list[str | int] | None | str | int = None,
    ):
        """Create a new JCalParsingError."""
        if path is None:
            path = []
        elif not isinstance(path, list):
            path = [path]
        self.path = path
        if not isinstance(parser, str):
            parser = parser.__name__
        self.parser = parser
        self.message = message
        full_message = message
        repr_path = ""
        if path:
            repr_path = "".join([f"[{index}]" for index in path])
            full_message = f"{repr_path}: {full_message}"
            repr_path += " "
        if parser:
            full_message = f"{repr_path}in {parser}: {message}"
        super().__init__(full_message)

    @classmethod
    @contextlib.contextmanager
    def reraise_with_path_added(cls, *path_components: int | str):
        """Automatically re-raise the exception with path components added."""
        try:
            yield
        except JCalParsingError as e:
            raise cls(
                path=list(path_components) + e.path, parser=e.parser, message=e.message
            ) from e


__all__ = [
    "ComponentEndMissing",
    "ComponentStartMissing",
    "FeatureWillBeRemovedInFutureVersion",
    "IncompleteAlarmInformation",
    "IncompleteComponent",
    "InvalidCalendar",
    "JCalParsingError",
    "LocalTimezoneMissing",
]
