from typing import Any

from icalendar.compatibility import Self
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode


class vInline(str):
    """This is an especially dumb class that just holds raw unparsed text and
    has parameters. Conversion of inline values are handled by the Component
    class, so no further processing is needed.
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
        if "\r" in value or "\n" in value:
            raise ValueError(
                f"An inline value may not contain CR or LF characters: {value!r}"
            )
        self = super().__new__(cls, value)
        self.params = Parameters(params)
        return self

    def to_ical(self) -> bytes:
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        return cls(ical)

    @property
    def ical_value(self) -> str:
        """The raw, unparsed text of the inline value.

        The text is returned as a plain :class:`str`. It's neither split
        into its separate values nor unescaped.

        Example:
            ..  code-block:: pycon

                >>> from icalendar.prop import vInline
                >>> vInline("Chair,Table").ical_value
                'Chair,Table'

        ..  seealso::

            :rfc:`5545#section-3.1.2` for multiple values in one property.
        """
        return str(self)


__all__ = ["vInline"]
