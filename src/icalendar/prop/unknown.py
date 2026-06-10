"""UNKNOWN values from :rfc:`7265`.

:class:`vUnknown` is a deliberate near-duplicate of
:class:`~icalendar.prop.text.vText`. It does **not** inherit from ``vText`` even
though most of the plumbing is identical: the one method that differs,
:meth:`vUnknown.to_ical`, is the entire reason the class exists, and inheriting
from ``vText`` is what made the value get re-escaped (see :rfc:`7265#section-5.1`).
Keeping them as separate classes stops that from silently coming back.
"""

from typing import Any, ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import DEFAULT_ENCODING, ICAL_TYPE, to_unicode


class vUnknown(str):
    r"""A property value of the :rfc:`7265` reserved ``unknown`` type.

    Unlike :class:`~icalendar.prop.text.vText`, the value is preserved
    **verbatim** -- taken into and out of iCalendar without :rfc:`5545` escaping
    or unescaping. The real value type of an unrecognized property is not known,
    so no escaping rules can be applied and the value must round-trip
    byte-for-byte (:rfc:`7265#section-5.1`).
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
        return f"vUnknown({self.to_ical()!r})"

    def to_ical(self) -> bytes:
        r"""Return the value verbatim, without :rfc:`5545` escaping (:rfc:`7265#section-5.2`).

        This is the one place ``vUnknown`` deliberately differs from
        :class:`~icalendar.prop.text.vText`, whose ``to_ical`` escapes ``;`` ``,``
        ``\\`` and newlines.
        """
        return self.encode(self.encoding)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE) -> Self:
        """Take the value verbatim, without unescaping."""
        return cls(ical)

    @property
    def ical_value(self) -> str:
        """The string value of the property."""
        return str(self)

    from icalendar.param import ALTREP, GAP, LANGUAGE, RELTYPE, VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`.

        The value is passed through unchanged. The type field is the lowercased
        ``VALUE`` -- ``"unknown"`` by default, or a preserved unrecognized value
        type if one was set.
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
