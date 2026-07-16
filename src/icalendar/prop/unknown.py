"""UNKNOWN values from :rfc:`7265`."""

from typing import TYPE_CHECKING, Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode

if TYPE_CHECKING:
    from icalendar.parser.content_line import Contentline


class vUnknown(str):
    """A property value of the :rfc:`7265#section-5` reserved UNKNOWN value data type.

    ..  versionchanged:: 7.2.0

        Previously ``vUnknown`` inherited from ``vText``, which unescapes values.
        Now ``vUnknown`` doesn't unescape its values, which is the correct behavior.

    Unlike :class:`~icalendar.prop.text.vText`, the value is preserved verbatim
    when imported from and exported to iCalendar data, without :rfc:`5545` escaping
    or unescaping. When the value type of an unrecognized property is not known,
    then no escaping rules can be applied, and the value must be preserved as is
    round-trip.

    See also:

        :rfc:`7265#section-5.1`
    """

    default_value: ClassVar[str] = "UNKNOWN"
    params: Parameters
    __slots__ = ("encoding", "params")

    def __new__(
        cls,
        value: ICAL_TYPE,
        encoding: str = DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ) -> Self:
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.encoding = encoding
        self.params = Parameters(params)
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_ical()!r})"

    def to_ical(self) -> bytes:
        r"""Return the value verbatim, without :rfc:`5545` escaping.

        This method's implementation is different from that in
        :class:`~icalendar.prop.text.vText`, whose
        :meth:`~icalendar.prop.text.vText.to_ical` method escapes ``;``, ``,``,
        ``\``, and newlines.

        Example:

            The semicolon is kept verbatim for UNKNOWN, unlike a TEXT value
            which would escape it as ``\\;``.

            .. code-block:: pycon

                >>> from icalendar.prop import vText, vUnknown
                >>> vUnknown("a;b").to_ical()
                b'a;b'
                >>> vText("a;b").to_ical()
                b'a\\;b'

        See also:

            :rfc:`7265#section-5.2`

        """
        return self.encode(self.encoding)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        """Take the value verbatim, without unescaping."""
        return cls(ical)

    @classmethod
    def initialize_with_raw_content_line(cls, line: "Contentline") -> str:
        """Return this type's value from ``line``, taken verbatim.

        Value types that must not have their value unescaped provide this
        method, and the parser uses it to obtain the value instead of
        :meth:`~icalendar.parser.content_line.Contentline.parts`. For
        :rfc:`7265` ``UNKNOWN`` values, the escaping rules of the real value
        type are not known, so no unescaping can be applied.
        """
        return line.raw_parts()[2]

    @property
    def ical_value(self) -> str:
        """The string value of the property."""
        return str(self)

    from icalendar.param import ALTREP, GAP, LANGUAGE, RELTYPE, VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property, according to :rfc:`7265#section-5.1`.

        If the property doesn't include a VALUE property parameter and its value
        type is not known, then its value type is set to ``"unknown"``. Else the
        property's value type is converted to lowercase.

        The property's value is the unprocessed value text, aside from standard
        JSON string escaping.
        """
        return [name, self.params.to_jcal(), self.VALUE.lower(), str(self)]

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vUnknown."""
        return [cls("Some property text.")]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`, taking the value verbatim.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        string = jcal_property[3]
        JCalParsingError.validate_value_type(string, str, cls, 3)
        return cls(
            string,
            params=Parameters.from_jcal_property(jcal_property),
        )

    @classmethod
    def parse_jcal_value(cls, jcal_value: Any) -> Self:
        """Parse a jCal value into a vUnknown."""
        JCalParsingError.validate_value_type(jcal_value, (str, int, float), cls)
        return cls(str(jcal_value))


__all__ = ["vUnknown"]
