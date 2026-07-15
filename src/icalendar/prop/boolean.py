"""BOOLEAN values from :rfc:`5545`."""

from typing import Any, ClassVar

from icalendar.caselessdict import CaselessDict
from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters


class vBoolean(int):
    """An iCalendar boolean value.

    Converts between iCalendar ``BOOLEAN`` value types and Python boolean values.
    In iCalendar data, boolean values are represented as "TRUE" or "FALSE". Values
    parsed from iCalendar text are case insensitive. ``True``, ``true``, and ``TRUE``
    are all accepted when converting from iCalendar to Python.

    Conforming with :rfc:`5545#section-3.3.2`, boolean values are represented in
    iCalendar data as either ``TRUE`` or ``FALSE``.

    Example:
        Parse and create iCalendar boolean values.

        .. code-block:: pycon

            >>> from icalendar.prop import vBoolean
            >>> boolean = vBoolean.from_ical('TRUE')
            >>> boolean
            True

            >>> boolean = vBoolean.from_ical('fAlse')
            >>> boolean
            False

            >>> vBoolean(True).to_ical()
            b'TRUE'
    """

    default_value: ClassVar[str] = "BOOLEAN"
    params: Parameters

    BOOL_MAP = CaselessDict({"true": True, "false": False})

    def __new__(
        cls, *args: Any, params: dict[str, Any] | None = None, **kwargs: Any
    ) -> Self:
        self = super().__new__(cls, *args, **kwargs)
        self.params = Parameters(params)
        return self

    def to_ical(self) -> bytes:
        """Converts a :class:`~icalendar.prop.boolean.vBoolean` to a BOOLEAN property type.

        This class method takes a ``vBoolean``—a Python boolean value—and converts it to an iCalendar BOOLEAN property type, in compliance with :rfc:`5545#section-3.3.2`.

        Returns:
            Either "TRUE" or "FALSE" as bytes, depending on the value of the ``vBoolean``.
        """
        return b"TRUE" if self else b"FALSE"

    @property
    def ical_value(self) -> bool:
        """BOOLEAN property type according to :rfc:`5545#section-3.3.2`"""
        return bool(self)

    @classmethod
    def from_ical(cls, ical: str) -> bool:
        try:
            return cls.BOOL_MAP[ical]
        except Exception as e:
            raise ValueError(f"Expected 'TRUE' or 'FALSE'. Got {ical}") from e

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vBoolean."""
        return [
            cls(True),
            cls(False),
        ]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), bool(self)]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265` to a vBoolean.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], bool, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )


__all__ = ["vBoolean"]
