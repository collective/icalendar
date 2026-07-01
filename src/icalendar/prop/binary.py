"""BINARY values from :rfc:`5545`."""

import base64
import binascii
from typing import ClassVar

from icalendar.compatibility import Self, deprecate_for_version_8
from icalendar.error import JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import to_unicode


class vBinary:
    """Binary property values are Base64 encoded."""

    default_value: ClassVar[str] = "BINARY"
    params: Parameters
    bytes: bytes
    """The raw binary value of the BINARY property.

    This is the authoritative storage and round-trips losslessly, including
    for non-UTF-8 data. Use this instead of the deprecated :attr:`obj`.
    """

    def __init__(self, obj: str | bytes, params: dict[str, str] | None = None) -> None:
        if isinstance(obj, str):
            self.bytes = obj.encode("utf-8")
        else:
            self.bytes = obj
        self.params = Parameters(encoding="BASE64", value="BINARY")
        if params:
            self.params.update(params)

    def __repr__(self) -> str:
        return f"vBinary({self.to_ical()})"

    def to_ical(self) -> bytes:
        return base64.b64encode(self.bytes)

    @staticmethod
    def from_ical(ical: str | bytes) -> bytes:
        try:
            return base64.b64decode(ical, validate=True)
        except (binascii.Error, ValueError) as e:
            raise ValueError("Not valid base 64 encoding.") from e

    @property
    @deprecate_for_version_8
    def obj(self) -> str:
        """Deprecated string view of the value.

        .. deprecated:: 7.1.3
            Use :attr:`bytes` for the raw binary value. ``obj`` decodes
            :attr:`bytes` as text and is lossy for non-UTF-8 data. It will
            be removed in icalendar 8.
        """
        return to_unicode(self.bytes)

    @obj.setter
    @deprecate_for_version_8
    def obj(self, value: str | bytes) -> None:
        self.bytes = value.encode("utf-8") if isinstance(value, str) else value

    def __eq__(self, other: object) -> bool:
        """self == other"""
        return isinstance(other, vBinary) and self.bytes == other.bytes

    def __hash__(self) -> int:
        """Hash of the vBinary object."""
        return hash(self.bytes)

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
        return [
            name,
            params,
            self.VALUE.lower(),
            base64.b64encode(self.bytes).decode("ascii"),
        ]

    @property
    def ical_value(self) -> bytes:
        """The raw ``bytes`` value of the BINARY property.

        .. versionadded:: 7.1.0

        .. versionchanged:: 7.1.3
            Returns the raw stored bytes. Previously the stored value was
            Base64-decoded, which raised :class:`ValueError` for non-Base64
            input. See :pr:`1356`.
        """
        return self.bytes

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
            cls.from_ical(jcal_property[3]),
            params=Parameters.from_jcal_property(jcal_property),
        )


__all__ = ["vBinary"]
