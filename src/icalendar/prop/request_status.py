"""vRequestStatus is a subclass of vText with convenience methods."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from icalendar.error import JCalParsingError
from icalendar.parser.parameter import Parameters

from .text import vText

if TYPE_CHECKING:
    from collections.abc import Sequence

    from icalendar.compatibility import Self

REQUEST_STATUS_GRAMMAR = re.compile(
    r"^(?P<code>[\d\.]*)"
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
    def code(self) -> tuple[int, ...]:
        """Return the status code as a tuple.

        Returns:
            A tuple of integers or () if the status code could not be parsed.
        """
        return tuple(int(x) for x in self.code_string.split(".") if x)

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
        code: Sequence[int] | str | int,
        description: str = "",
        data: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> Self:
        """Create a new request status object.

        Parameters:
            code: The status code.
            description: The description of the request status.
            data: The data of the request status.

        Returns:
            A new request status object.
        """
        if isinstance(code, int):
            code = (code,)
        if not isinstance(code, str):
            code = ".".join(str(x) for x in code)
        description = ESCAPE.sub(r"\\\1", description)
        request_status = f"{code};{description}"
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
            code=status_list[0] if len(status_list) > 0 else (),
            description=status_list[1] if len(status_list) > 1 else "",
            data=";".join(status_list[2:]) if len(status_list) > 2 else None,
            params=Parameters.from_jcal_property(jcal_property),
        )


__all__ = ["vRequestStatus"]
