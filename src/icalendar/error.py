"""Errors thrown by icalendar."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


class InvalidCalendar(ValueError):
    """The calendar given is not valid.

    This calendar does not conform with RFC 5545 or breaks other RFCs.
    """


class ICalParsingError(InvalidCalendar):
    """Could not parse an iCalendar."""

    def __init__(
        self,
        message: str,
        line: str | None = None,
        line_number: int | None = None,
        value: object = None,
    ) -> None:
        self.message = message
        self.line = line
        self.line_number = line_number
        self.value = value

        full_message = message

        if value is not None:
            full_message += f": {value!r}"

        if line_number is not None and line is not None:
            full_message += f" (line {line_number}: {line!r})"
        elif line_number is not None:
            full_message += f" (line {line_number})"
        elif line is not None:
            full_message += f" ({line!r})"

        super().__init__(full_message)


class BrokenCalendarProperty(InvalidCalendar):
    """A property could not be parsed and its value is broken.

    This error is raised when accessing attributes on a
    :class:`~icalendar.prop.vBroken` property that would normally
    be present on the expected type. The original parse error
    is chained as ``__cause__``.
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


def _repr_index(index: str | int) -> str:
    """Create a JSON compatible representation for the index.

    Parameters:
        index: It is either a dict key (string) or a list position (integer).

    Returns:
        The index as a quoted string if it's a string, else the string
        representation if it's an integer.
    """
    if isinstance(index, str):
        return f'"{index}"'
    return str(index)


class JCalParsingError(InvalidCalendar):
    """Could not parse a part of the JCal."""

    _default_value = object()

    def __init__(
        self,
        message: str,
        parser: str | type = "",
        path: list[str | int] | None | str | int = None,
        value: object = _default_value,
    ) -> None:
        """Create a new JCalParsingError.

        Parameters:
            message: A description of the error that occurred while parsing.
            parser: The parser class or its name where the error occurred.
            path: The location in the jCal structure where the error occurred.
            value: The value which caused the error, if available.
        """
        self.path = self._get_path(path)
        if not isinstance(parser, str):
            parser = parser.__name__
        self.parser = parser
        self.message = message
        self.value = value
        full_message = message
        repr_path = ""
        if self.path:
            repr_path = "".join([f"[{_repr_index(index)}]" for index in self.path])
            full_message = f"{repr_path}: {full_message}"
            repr_path += " "
        if parser:
            full_message = f"{repr_path}in {parser}: {message}"
        if value is not self._default_value:
            full_message += f" Got value: {value!r}"
        super().__init__(full_message)

    @classmethod
    @contextlib.contextmanager
    def reraise_with_path_added(
        cls,
        *path_components: int | str,
    ) -> Generator[None, None, None]:
        """Automatically re-raise the exception with path components added.

        Raises:
            ~error.JCalParsingError: If there was an exception in the context.
        """
        try:
            yield
        except JCalParsingError as e:
            raise cls(
                path=list(path_components) + e.path,
                parser=e.parser,
                message=e.message,
                value=e.value,
            ).with_traceback(e.__traceback__) from e

    @staticmethod
    def _get_path(path: list[str | int] | None | str | int) -> list[str | int]:
        """Return the path as a list."""
        if path is None:
            path = []
        elif not isinstance(path, list):
            path = [path]
        return path

    @classmethod
    def validate_property(
        cls,
        jcal_property: list[object],
        parser: str | type,
        path: list[str | int] | None | str | int = None,
    ) -> None:
        """Validate a jCal property.

        Parameters:
            jcal_property: A list with at least four items (name,
                parameters, value type, and value) which is the jCal property
                to be validated.
            parser: The parser class or its name where the error occurred.
            path: The location in the jCal structure where the error occurred.

        Raises:
            ~error.JCalParsingError: if the property is not valid.
        """
        path = cls._get_path(path)
        if not isinstance(jcal_property, list) or len(jcal_property) < 4:
            raise JCalParsingError(
                "The property must be a list with at least 4 items.",
                parser,
                path,
                value=jcal_property,
            )
        if not isinstance(jcal_property[0], str):
            raise JCalParsingError(
                "The name must be a string.", parser, path + [0], value=jcal_property[0]
            )
        if not isinstance(jcal_property[1], dict):
            raise JCalParsingError(
                "The parameters must be a mapping.",
                parser,
                path + [1],
                value=jcal_property[1],
            )
        if not isinstance(jcal_property[2], str):
            raise JCalParsingError(
                "The VALUE parameter must be a string.",
                parser,
                path + [2],
                value=jcal_property[2],
            )

    _type_names = {
        str: "a string",
        int: "an integer",
        float: "a float",
        bool: "a boolean",
    }

    @classmethod
    def validate_value_type(
        cls,
        jcal: object,
        expected_type: type[str | int | float | bool]
        | tuple[type[str | int | float | bool], ...],
        parser: str | type = "",
        path: list[str | int] | None | str | int = None,
    ) -> None:
        """Validate the type of a jCal value."""
        if not isinstance(jcal, expected_type):
            type_name = (
                cls._type_names[expected_type]
                if isinstance(expected_type, type)
                else " or ".join(cls._type_names[t] for t in expected_type)
            )
            raise cls(
                f"The value must be {type_name}.",
                parser=parser,
                value=jcal,
                path=path,
            )

    @classmethod
    def validate_list_type(
        cls,
        jcal: object,
        expected_type: type[str | int | float | bool],
        parser: str | type = "",
        path: list[str | int] | None | str | int = None,
    ) -> None:
        """Validate the type of each item in a jCal list."""
        path = cls._get_path(path)
        if not isinstance(jcal, list):
            raise cls(
                "The value must be a list.",
                parser=parser,
                value=jcal,
                path=path,
            )
        for index, item in enumerate(jcal):
            if not isinstance(item, expected_type):
                type_name = cls._type_names[expected_type]
                raise cls(
                    f"Each item in the list must be {type_name}.",
                    parser=parser,
                    value=item,
                    path=path + [index],
                )


__all__ = [
    "BrokenCalendarProperty",
    "ComponentEndMissing",
    "ComponentStartMissing",
    "FeatureWillBeRemovedInFutureVersion",
    "ICalParsingError",
    "IncompleteAlarmInformation",
    "IncompleteComponent",
    "InvalidCalendar",
    "JCalParsingError",
    "LocalTimezoneMissing",
]
