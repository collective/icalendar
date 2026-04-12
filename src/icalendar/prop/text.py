"""TEXT values from :rfc:`5545`."""

from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters, _escape_char
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode


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

    When the TEXT object is serialized to an icalendar stream, certain
    characters are escaped or changed.
    These characters include the COMMA, SEMICOLON, BACKSLASH, and line breaks.

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
        """Create a new :class:`~icalendar.prop.text.vText` instance.

        This method overrides :py:meth:`str.__new__` because TEXT values
        inherit from :class:`str`, which is immutable. The ``__new__`` method
        decodes bytes if needed, creates the string instance, and attaches
        encoding metadata and iCalendar property parameters.

        Parameters:
            value: Raw text passed to :func:`~icalendar.parser_tools.to_unicode`
                before constructing the :class:`str` value.
            encoding: Encoding used when ``value`` is :class:`bytes`.
            params: Optional property parameters according to :rfc:`5545`.

        Returns:
            A new :class:`~icalendar.prop.text.vText` instance with
            associated parameters.

        Examples:
            .. code-block:: pycon

                >>> from icalendar.prop import vText
                >>> t = vText("Hello", params={"LANGUAGE": "en"})
                >>> str(t)
                'Hello'
                >>> t.encoding
                'utf-8'
                >>> t.params
                Parameters({'LANGUAGE': 'en'})
        """
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.encoding = encoding
        self.params = Parameters(params)
        return self

    def __repr__(self) -> str:
        return f"vText({self.to_ical()!r})"

    def to_ical(self) -> bytes:
        return _escape_char(self).encode(self.encoding)

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
