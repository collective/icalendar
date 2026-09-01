"""TEXT values from :rfc:`5545`."""

import re
from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters, _escape_char
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode

# :rfc:`5545#section-3.3.11` defines TEXT as
# ``*(TSAFE-CHAR / ":" / DQUOTE / ESCAPED-CHAR)`` where TSAFE-CHAR is in turn
# defined by the following grammar in :rfc:`5545#section-3.1`.
#
# ..  code-block:: text
#
#     TSAFE-CHAR = WSP / %x21 / %x23-2B / %x2D-39 / %x3C-5B /
#              %x5D-7E / NON-US-ASCII
#        ; Any character except CONTROLs not needed by the current
#        ; character set, DQUOTE, ";", ":", "\", ","
#
# CONTROL is defined in the same section as ``%x00-08 / %x0A-1F / %x7F``, so no
# control character except the horizontal tab may appear in a TEXT value.
# The line feed, ``\x0a``, is additionally accepted here because it is the
# result of the escaped sequences ``\N`` and ``\n``.
_UNSAFE_TEXT_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")


def _strip_unsafe_text_chars(value: object) -> str:
    r"""Remove CONTROL characters that :rfc:`5545#section-3.3.11` forbids in TEXT.

    ``\\r\\n`` and a lone ``\\r`` become ``\\n`` first so an intentional line
    break is kept and escaped on serialize. Remaining matches of
    :data:`_UNSAFE_TEXT_CHARS` (NUL, other C0 controls, DEL) are stripped.
    HTAB and LF are left as-is.

    :func:`~icalendar.parser_tools.to_unicode` leaves non-``str``/``bytes``
    values unchanged, and callers such as :meth:`vUid.new` pass a
    :class:`uuid.UUID`. Coerce those to ``str`` the same way ``str.__new__``
    did before this filter ran.
    """
    if not isinstance(value, str):
        value = str(value)
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return _UNSAFE_TEXT_CHARS.sub("", value)


class vText(str):
    r"""vText is a data type that contains human-readable text values.

    The vText property uses the :rfc:`5545#section-3.3.11` TEXT value type
    in various icalendar properties to show free-form text that others can read.
    This class can be created from Python strings, and can be used to add text
    descriptions to calendar events.

    To create a TEXT object, pass in the string you want when creating the
    object.

    To add a line break, use ``\n`` or ``\N``.

    Use the LANGUAGE property parameter to set the language of the text.

    When the TEXT object is created, CONTROL characters other than HTAB
    are removed so both :meth:`to_ical` and :meth:`to_jcal` stay valid
    :rfc:`5545` TEXT. Parsing does not raise; the value is corrected.
    When the TEXT object is serialized to an icalendar stream, COMMA,
    SEMICOLON, BACKSLASH, and line breaks are escaped.

    Contrast TEXT with the UNKNOWN value data type specified in :rfc:`7265#section-5`.
    UNKNOWN is implemented in the Python class :class:`~icalendar.prop.unknown.vUnknown`,
    which does **not** apply this escaping and preserves its value verbatim,
    because the escaping rules of an unrecognized value type are not known.
    :class:`~icalendar.prop.unknown.vUnknown` deliberately does not inherit from
    ``vText``, so the two don't share escaping behavior.

    Examples:

        vText property as a TEXT value type.

        .. code-block:: text

            Project XYZ Final Review\nConference Room - 3B\nCome Prepared.

        Create a vText property, and display it in a readable format.

        .. code-block:: pycon

            >>> from icalendar.prop import vText
            >>> desc = 'Project XYZ Final Review\nConference Room - 3B\nCome Prepared.'
            >>> text = vText(desc)
            >>> text
            vText(b'Project XYZ Final Review\\nConference Room - 3B\\nCome Prepared.')
            >>> print(text.ical_value)
            Project XYZ Final Review
            Conference Room - 3B
            Come Prepared.

        Add a SUMMARY to an event, then display its value as a vText property then in a readable format:

        .. code-block:: pycon

            >>> from icalendar import Event
            >>> event = Event()
            >>> event.add('SUMMARY', desc)
            >>> event['SUMMARY']
            vText(b'Project XYZ Final Review\\nConference Room - 3B\\nCome Prepared.')
            >>> print(event.to_ical().decode())
            BEGIN:VEVENT
            SUMMARY:Project XYZ Final Review\nConference Room - 3B\nCome Prepared.
            END:VEVENT

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
        value = _strip_unsafe_text_chars(to_unicode(value, encoding=encoding))
        self = super().__new__(cls, value)
        self.encoding = encoding
        self.params = Parameters(params)
        return self

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_ical()!r})"

    def to_ical(self) -> bytes:
        """Serialize this TEXT value with :rfc:`5545` escaping."""
        return _escape_char(self).encode(self.encoding)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        r"""Parse a TEXT value from its iCalendar representation.

        Control characters that :rfc:`5545#section-3.3.11` does not allow
        in TEXT do not raise. :meth:`__new__` removes them so the parsed
        object can still be read and later serialized.
        """
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
