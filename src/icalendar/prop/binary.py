"""BINARY values from :rfc:`5545`."""

import base64
import binascii
from typing import ClassVar

from icalendar.compatibility import Self
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import to_unicode


class _DecodedBinary(bytes):
    """Binary data decoded from an iCalendar value."""


class _EncodedBinary(str):
    """Base64 data read from an iCalendar or jCal value."""

    __slots__ = ()


class vBinary:
    """Binary property values are base 64 encoded."""

    default_value: ClassVar[str] = "BINARY"
    params: Parameters
    obj: str

    def __init__(self, obj: str | bytes, params: dict[str, str] | None = None) -> None:
        self.obj = (
            _EncodedBinary(base64.b64encode(obj).decode("ascii"))
            if isinstance(obj, _DecodedBinary)
            else to_unicode(obj)
        )
        self.params = Parameters(encoding="BASE64", value="BINARY")
        if params:
            self.params.update(params)

    def __repr__(self) -> str:
        return f"vBinary({self.to_ical()})"

    def to_ical(self) -> bytes:
        if isinstance(self.obj, _EncodedBinary):
            return self.obj.encode("ascii")
        return binascii.b2a_base64(self.obj.encode("utf-8"))[:-1]

    @staticmethod
    def from_ical(ical: str | bytes) -> bytes:
        try:
            return _DecodedBinary(base64.b64decode(ical, validate=True))
        except (binascii.Error, ValueError) as e:
            raise ValueError("Not valid base 64 encoding.") from e

    @property
    def base64data(self) -> str:
        """The Base64-encoded string view of this value.

        This is the same string that :meth:`to_ical` produces, exposed as
        a plain :class:`str` instead of :class:`bytes` so you don't need to
        call :func:`base64.b64encode` yourself. See :issue:`1550`.

        Returns:
            The Base64-encoded representation of the stored value.
        """
        return self.to_ical().decode("ascii")

    @base64data.setter
    def base64data(self, value: str) -> None:
        """Set this value from a Base64-encoded string.

        Parameters:
            value: A Base64-encoded string.

        Raises:
            ValueError: If ``value`` isn't valid Base64.
        """
        decoded = self.from_ical(value)
        self.obj = _EncodedBinary(base64.b64encode(decoded).decode("ascii"))

    def __eq__(self, other: object) -> bool:
        """self == other"""
        return isinstance(other, vBinary) and self.obj == other.obj

    def __hash__(self) -> int:
        """Hash of the vBinary object."""
        return hash(self.obj)

    @classmethod
    def examples(cls) -> list[Self]:
        """Examples of vBinary."""
        return [cls("VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4")]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        params = self.params.to_jcal()
        if params.get("encoding") == "BASE64":
            # BASE64 is the only allowed encoding
            del params["encoding"]
        return [name, params, self.VALUE.lower(), self.obj]

    @property
    def ical_value(self) -> bytes:
        """The bytes value of the BINARY property."""
        return self.from_ical(self.obj)

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265` to a vBinary.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], str, cls, 3)
        return cls(
            _EncodedBinary(jcal_property[3]),
            params=Parameters.from_jcal_property(jcal_property),
        )


__all__ = ["vBinary"]
