"""vRequestStatus is a subclass of vText with convenience methods."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .text import vText

if TYPE_CHECKING:
    from collections.abc import Sequence

    from icalendar.compatibility import Self

REQUEST_STATUS_GRAMMAR = re.compile(
    "^(?P<code>[^;]*)(?:;(?P<description>[^;]*)(?:;(?P<data>.*))?)?$", re.MULTILINE
)
UNESCAPE = re.compile(r"\\(.)")
ESCAPE = re.compile(r"([\\,;])")


class vRequestStatus(vText):
    """A text specifically for REQUEST-STATUS.

    See :rfc:`5545#section-3.8.8.3`.
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
        match = self._get_match()
        if not match:
            return ()
        code: str = match.group("code")
        return tuple(int(x) for x in code.split(".") if x)

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
        code: Sequence[int, ...] | str | int,
        description: str = "",
        data: str | None = None,
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
        return cls(request_status)

    @classmethod
    def examples(cls) -> list[Self]:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Examples of vRequestStatus."""
        return [
            cls("2.0;Success"),
            cls("3.7;Invalid calendar user;ATTENDEE:mailto:jsmith@example.org"),
        ]


__all__ = ["vRequestStatus"]
