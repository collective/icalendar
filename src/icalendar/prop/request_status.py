"""vRequestStatus is a subclass of vText with convenience methods."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from icalendar.error import InvalidCalendar, JCalParsingError
from icalendar.parser.parameter import Parameters

from .text import vText

if TYPE_CHECKING:
    from icalendar.compatibility import Self

CODE_REGEX = r"^[0-9]\.[0-9](?:\.[0-9])?$"
CODE_REGEX_PATTERN = re.compile(CODE_REGEX)

REQUEST_STATUS_GRAMMAR = re.compile(
    r"^(?P<code>[0-9]\.[0-9](?:\.[0-9])?)"
    r"(?:;(?P<description>(?:\\.|[^;\\])*)"
    r"(?:;(?P<data>.*))?)?$",
    re.MULTILINE,
)
UNESCAPE = re.compile(r"\\(.)")
ESCAPE = re.compile(r"([\\,;])")


class vRequestStatus(vText):
    """A text specifically for REQUEST-STATUS.

    See :rfc:`5545#section-3.8.8.3`.

    Example:

        .. code-block:: pycon

            >>> from icalendar.prop import vRequestStatus
            >>> r = vRequestStatus("2.0;Success")
            >>> r.code
            (2, 0)
            >>> r.description
            'Success'
            >>> r.data is None
            True

    """

    __match: re.Match | None = None

    def _get_match(self) -> re.Match | None:
        """Return a match for parsing."""
        if self.__match is None:
            self.__match = REQUEST_STATUS_GRAMMAR.match(self)
        return self.__match

    @property
    def code(self) -> tuple[int, int] | tuple[int, int, int] | tuple[()]:
        """Return the status code as a tuple.

        Returns:
            A tuple of integers or ``()`` if the status code could not be parsed.
        """
        s = self.code_string.split(".")
        if len(s) == 2:
            return int(s[0]), int(s[1])
        if len(s) == 3:
            return int(s[0]), int(s[1]), int(s[2])
        return ()

    @property
    def code_string(self) -> str:
        """Return the status code as a string.

        Returns:
            The status string or ``""`` if the request status could not be parsed.
        """
        match = self._get_match()
        if not match:
            return ""
        return match.group("code")

    def _unescape(self, string: str):
        """Unescape a string."""
        return UNESCAPE.sub(r"\1", string)

    @property
    def description(self) -> str:
        """Return the description of the request status.

        Returns:
            The description of the request status or ``""``
            if the request status could not be parsed.
        """
        match = self._get_match()
        if not match:
            return ""
        description: str = match.group("description") or ""
        return self._unescape(description)

    @property
    def data(self) -> str | None:
        """Return the data of the request status.

        Returns:
            The data of the request status or ``None``.
        """
        match = self._get_match()
        if not match:
            return None
        data: str = match.group("data")
        if data is None:
            return None
        return self._unescape(data)

    @classmethod
    def new(
        cls,
        code: tuple[int, int] | tuple[int, int, int] | str,
        description: str = "",
        data: str | None = None,
        *,
        params: dict[str, Any] | None = None,
        validate: bool = True,
    ) -> Self:
        """Create a new request status object.

        Parameters:
            code: The status code.
            description: The description of the request status.
            data: The data of the request status.
            validate: Turn validation for the ``code`` string on and off.
                      ``code`` tuples are always validated.

        Raises:
            InvalidCalendar: If the code is not valid.
            TypeError: If the code is neither a tuple of integers nor string.

        Returns:
            A new request status object.
        """
        if not isinstance(code, (tuple, str)):
            raise TypeError("code must be tuple or string")
        if isinstance(code, str):
            code_string = code
            if validate and CODE_REGEX_PATTERN.match(code_string) is None:
                raise InvalidCalendar(
                    f"code must have 2 or 3 numbers from 0 to 9. Got {code_string!r}"
                )
        else:
            if not all(isinstance(x, int) for x in code):
                raise TypeError(
                    f"code must be a tuple of 2 or 3 integers from 0 to 9. Got {code!r}"
                )
            if len(code) not in (2, 3) or not all(0 <= x <= 9 for x in code):
                raise InvalidCalendar(
                    f"code must have 2 or 3 numbers from 0 to 9. Got {code!r}"
                )
            code_string = f"{code[0]}.{code[1]}"
            if len(code) == 3:
                code_string += f".{code[2]}"
        description = ESCAPE.sub(r"\\\1", description)
        request_status = f"{code_string};{description}"
        if data is not None:
            data = ESCAPE.sub(r"\\\1", data)
            request_status += f";{data}"
        return cls(request_status, params=params)

    @classmethod
    def examples(cls) -> list[Self]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Examples of vRequestStatus."""
        return [
            cls("2.0;Success"),
            cls("3.7;Invalid calendar user;ATTENDEE:mailto:jsmith@example.org"),
        ]

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        status = [self.code_string, self.description, self.data]
        if status[-1] is None:
            status = status[:-1]
        return [name, self.params.to_jcal(), self.VALUE.lower(), status]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        status_list = jcal_property[3]
        JCalParsingError.validate_list_type(status_list, str, cls, 3)
        return cls.new(
            code=status_list[0] if len(status_list) > 0 else "",
            description=status_list[1] if len(status_list) > 1 else "",
            data=";".join(status_list[2:]) if len(status_list) > 2 else None,
            params=Parameters.from_jcal_property(jcal_property),
            validate=False,
        )


__all__ = ["vRequestStatus"]
