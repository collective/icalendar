"""INT values from :rfc:`5545`."""

from typing import Any, ClassVar
from xml.etree.ElementTree import Element, SubElement

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError, XCalParsingError
from icalendar.parser import Parameters
from icalendar.parser.xcal.adapter import ElementAdapter
from icalendar.parser.xcal.base import XCalParser
from icalendar.parser.xcal.wrapper import from_xcal_wrapper
from icalendar.parser_tools import ICAL_TYPE


class vInt(int):
    """Integer

    Value Name:
        INTEGER

    Purpose:
        This value type is used to identify properties that contain a
        signed integer value.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            integer    = (["+"] / "-") 1*DIGIT

    Description:
        If the property permits, multiple "integer" values are
        specified by a COMMA-separated list of values.  The valid range
        for "integer" is -2147483648 to 2147483647.  If the sign is not
        specified, then the value is assumed to be positive.

    The ``__new__`` method creates a vInt instance:

    Parameters:
        value: Integer value to encode. Must be within :attr:`min` to :attr:`max`.
        params: Optional parameter dictionary for the property.

    Returns:
        vInt instance

    Raises:
        ValueError: If the value is outside the RFC 5545 signed 32-bit integer range
            as defined in :attr:`min` and :attr:`max`.

    Examples:

        .. code-block:: text

            1234567890
            -1234567890
            +1234567890
            432109876

        .. code-block:: pycon

            >>> from icalendar.prop import vInt
            >>> integer = vInt.from_ical('1234567890')
            >>> integer
            1234567890
            >>> integer = vInt.from_ical('-1234567890')
            >>> integer
            -1234567890
            >>> integer = vInt.from_ical('+1234567890')
            >>> integer
            1234567890
            >>> integer = vInt.from_ical('432109876')
            >>> integer
            432109876

        Create a PRIORITY property (1 = highest priority):

        .. code-block:: pycon

            >>> priority = vInt(1)
            >>> priority
            1
            >>> priority.to_ical()
            b'1'

        Create SEQUENCE property (for versioning):

        .. code-block:: pycon

            >>> sequence = vInt(3)
            >>> sequence.to_ical()
            b'3'
    """

    default_value: ClassVar[str] = "INTEGER"
    params: Parameters

    min: ClassVar[int] = -2_147_483_648
    """min: The minimum valid value per :rfc:`5545#section-3.3.8` (``-2147483648``)."""
    max: ClassVar[int] = 2_147_483_647
    """max: The maximum valid value per :rfc:`5545#section-3.3.8` (``2147483647``)."""

    def __new__(
        cls,
        *args,
        params: dict[str, Any] | None = None,
        _validate_range: bool = True,
        **kwargs,
    ):
        self = super().__new__(cls, *args, **kwargs)
        self.params = Parameters(params)
        if not (cls.min <= self <= cls.max) and _validate_range:
            raise ValueError(
                f"Integer {self} is outside the RFC 5545 range [{cls.min}, {cls.max}]"
            )
        return self

    def to_ical(self) -> bytes:
        return str(self).encode("utf-8")

    @property
    def ical_value(self) -> int:
        """INTEGER property type according to :rfc:`5545#section-3.3.8`"""
        return int(self)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE):
        try:
            value = int(ical)
        except Exception as e:
            raise ValueError(f"Expected int, got: {ical}") from e
        return cls(value)

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vInt."""
        return [cls(1000), cls(-42)]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), int(self)]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], int, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )

    @classmethod
    def parse_jcal_value(cls, value: Any) -> int:
        """Parse a jCal value for vInt.

        Raises:
            ~error.JCalParsingError: If the value is not an int.
        """
        JCalParsingError.validate_value_type(value, int, cls)
        return cls(value)

    @classmethod
    @from_xcal_wrapper
    def from_xcal(cls, parser: XCalParser, params: Parameters) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            element: The xCal element to parse.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        element = parser.parse_tag(cls.default_value)
        return cls.from_xcal_element(element, params)

    XCAL_TYPE = "xsd:integer"

    @classmethod
    def from_xcal_element(cls, element: ElementAdapter, params: Parameters) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            element: The xCal element to parse.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        try:
            value = int(element.get_xsd_token())
        except (TypeError, ValueError) as e:
            raise XCalParsingError(
                f"Expected {cls.XCAL_TYPE}",
                element.get_xsd_token(),
                element,
            ) from e
        # xCal integers are xsd:integers. They do not have a value range.
        return cls(value, params=params, _validate_range=False)

    @classmethod
    @from_xcal_wrapper
    def from_xcal_in_recur(cls, parser: XCalParser, params: Parameters) -> Self:
        """Parse xCal from :rfc:`6321`.

        Parameters:
            element: The xCal element to parse.

        Raises:
            ~error.XCalParsingError: If the provided xCal is invalid.
        """
        element = parser.parse_tag()
        return cls.from_xcal_element(element, params)

    def to_xcal(self, element: Element) -> None:
        """Add the xCal representation of this property according to :rfc:`6321`."""
        self.params.to_xcal(element)
        element = SubElement(element, self.default_value.lower())
        element.text = self.to_ical().decode()


class vNonNegativeInt(vInt):
    """This is an integer that is supposed to be at least 0.

    See https://www.rfc-editor.org/rfc/inline-errata/rfc6321.html#btn_3050
    """

    min: ClassVar[int] = 0

    @classmethod
    def examples(cls) -> list[vInt]:
        """Examples of vPositiveInt."""
        return [cls(1000), cls(0)]

    XCAL_TYPE = "xsd:positiveInteger"


__all__ = ["vInt", "vNonNegativeInt"]
