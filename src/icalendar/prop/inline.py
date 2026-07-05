from typing import Any

from icalendar.compatibility import Self
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode


class vInline(str):
    """A raw, unparsed inline property value that passes through unchanged.

    This class holds property values that icalendar does not parse further.
    The :class:`~icalendar.cal.component.Component` class handles conversion
    of these inline values, so no additional processing occurs here.

    Example:
        .. code-block:: pycon

            >>> from icalendar.prop import vInline
            >>> value = vInline("raw text")
            >>> value.to_ical()
            b'raw text'
            >>> vInline.from_ical("raw text")
            'raw text'
    """

    params: Parameters
    __slots__ = ("params",)

    def __new__(
        cls,
        value: ICAL_TYPE,
        encoding: str = DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ) -> Self:
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.params = Parameters(params)
        return self

    def to_ical(self) -> bytes:
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        return cls(ical)


__all__ = ["vInline"]
