"""TEXT values from :rfc:`5545`."""

from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters, escape_char
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode


class vText(str):
    """Text
    
    Value Name:
        TEXT
    
    Purpose:
        This value type is used to identify values that contain
        human-readable text.
    
    Format Definition:
        This value type is defined by the following notation:

        text       = *(TSAFE-CHAR / ":" / DQUOTE / ESCAPED-CHAR)
        ; Folded according to description above

        ESCAPED-CHAR = ("\\" / "\;" / "\," / "\N" / "\n")
        ; \\ encodes \, \N or \n encodes newline
        ; \; encodes ;, \, encodes ,

        TSAFE-CHAR = WSP / %x21 / %x23-2B / %x2D-39 / %x3C-5B /
                %x5D-7E / NON-US-ASCII
        ; Any character except CONTROLs not needed by the current
        ; character set, DQUOTE, ";", ":", "\", ","
    
    Description:
        If the property permits, multiple TEXT values are
        specified by a COMMA-separated list of values.

        The language in which the text is represented can be controlled by
        the "LANGUAGE" property parameter.

        An intentional formatted text line break MUST only be included in
        a "TEXT" property value by representing the line break with the
        character sequence of BACKSLASH, followed by a LATIN SMALL LETTER
        N or a LATIN CAPITAL LETTER N, that is "\n" or "\N".

        The "TEXT" property values may also contain special characters
        that are used to signify delimiters, such as a COMMA character for
        lists of values or a SEMICOLON character for structured values.
        In order to support the inclusion of these special characters in
        "TEXT" property values, they MUST be escaped with a BACKSLASH
        character.  A BACKSLASH character in a "TEXT" property value MUST
        be escaped with another BACKSLASH character.  A COMMA character in
        a "TEXT" property value MUST be escaped with a BACKSLASH
        character.  A SEMICOLON character in a "TEXT" property value MUST
        be escaped with a BACKSLASH character.  However, a COLON character
        in a "TEXT" property value SHALL NOT be escaped with a BACKSLASH
        character.

    Parameters:
        value: Text value to encode
        encoding: The encoding to use when encoding the value
        params: Optional parameter dictionary for the property
    
    Returns:
        vText instance
    
    Example:  A multiple line value of:

        Project XYZ Final Review
        Conference Room - 3B
        Come Prepared.

        would be represented as:

        Project XYZ Final Review\nConference Room - 3B\nCome Prepared.
    """

    default_value: ClassVar[str] = "TEXT"
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
        return f"vText({self.to_ical()!r})"

    def to_ical(self) -> bytes:
        return escape_char(self).encode(self.encoding)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        return cls(ical)

    @property
    def ical_value(self) -> str:
        """The string value of the text."""
        return str(self)

    from icalendar.param import ALTREP, GAP, LANGUAGE, RELTYPE, VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        if name == "request-status":  # TODO: maybe add a vRequestStatus class?
            return [name, {}, "text", self.split(";", 2)]
        return [name, self.params.to_jcal(), self.VALUE.lower(), str(self)]

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vText."""
        return [cls("Hello World!")]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        name = jcal_property[0]
        if name == "categories":
            from icalendar.prop import vCategory

            return vCategory.from_jcal(jcal_property)
        string = jcal_property[3]  # TODO: accept list or string but join with ;
        if name == "request-status":  # TODO: maybe add a vRequestStatus class?
            JCalParsingError.validate_list_type(jcal_property[3], str, cls, 3)
            string = ";".join(jcal_property[3])
        JCalParsingError.validate_value_type(string, str, cls, 3)
        return cls(
            string,
            params=Parameters.from_jcal_property(jcal_property),
        )

    @classmethod
    def parse_jcal_value(cls, jcal_value: Any) -> Self:
        """Parse a jCal value into a vText."""
        JCalParsingError.validate_value_type(jcal_value, (str, int, float), cls)
        return cls(str(jcal_value))


__all__ = ["vText"]
