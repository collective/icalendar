"""Parsing error value preservation."""


from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.prop.text import vText


class vBrokenProperty(vText):
    """Property that failed to parse, preserving raw value as text.

    Represents property values that failed to parse with their expected
    type. The raw iCalendar string is preserved for round-trip serialization.
    """

    default_value: ClassVar[str] = "TEXT"
    __slots__ = ("expected_type", "parse_error", "property_name")

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
        expected_type: str | None = None,
        property_name: str | None = None,
        parse_error: str | None = None,
    ):
        self = super().__new__(cls, value, encoding, params=params)
        object.__setattr__(self, "expected_type", expected_type)
        object.__setattr__(self, "property_name", property_name)
        object.__setattr__(self, "parse_error", parse_error)
        return self

    def __repr__(self) -> str:
        return (
            f"vBrokenProperty({str(self)!r}, "
            f"expected_type={self.expected_type!r}, "
            f"property_name={self.property_name!r})"
        )

    @classmethod
    def from_parse_error(
        cls,
        raw_value: str,
        params: Parameters,
        property_name: str,
        expected_type: str,
        error: Exception,
    ):
        """Create vBrokenProperty from parse failure."""
        return cls(
            raw_value,
            params=params,
            expected_type=expected_type,
            property_name=property_name,
            parse_error=str(error),
        )

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vBrokenProperty."""
        return [
            cls(
                "INVALID-DATE",
                expected_type="date-time",
                property_name="DTSTART",
                parse_error="Invalid date format",
            )
        ]

__all__ = ["vBrokenProperty"]
