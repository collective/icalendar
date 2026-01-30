"""This contains the IMAGE property from :rfc:`7986`."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from icalendar.prop.binary import vBinary
from icalendar.prop.uri import vUri

if TYPE_CHECKING:
    from icalendar.prop.text import vText


class Image:
    """An image represented as a URI or binary data according to RFC 7986.

    This property specifies an image for an iCalendar object or calendar
    component, either via a URI reference or inline binary data. Calendar
    user agents may use this image when presenting calendar data to users.

    Multiple Image properties may be used to specify alternative images
    with different media subtypes, resolutions, or sizes. When multiple
    images are present, user agents should select the most appropriate
    one or display none.

    Args:
        uri (str | None): URI pointing to the image resource.
        b64data (str | None): Base64-encoded binary image data.
        fmttype (str | None): Media type of the image (e.g. ``"image/png"``).
        altrep (str | None): Alternate representation link target.
        display (str | None): Intended display mode (e.g. ``"BADGE"``).
    """

    @classmethod
    def from_property_value(cls, value: vUri | vBinary | vText):
        """Create an Image instance from an iCalendar property value.

        Args:
            value (vUri | vBinary | vText): Property value containing image data
                or a reference to it.

        Returns:
            Image: A new Image instance created from the property value.

        Raises:
            TypeError: If the value type is not URI or BINARY.
        """
        params: dict[str, str] = {}
        if not hasattr(value, "params"):
            raise TypeError("Value must be URI or BINARY.")
        value_type = value.params.get("VALUE", "").upper()
        if value_type == "URI" or isinstance(value, vUri):
            params["uri"] = str(value)
        elif isinstance(value, vBinary):
            params["b64data"] = value.obj
        elif value_type == "BINARY":
            params["b64data"] = str(value)
        else:
            raise TypeError(
                f"The VALUE parameter must be URI or BINARY, not {value_type!r}."
            )
        params.update(
            {
                "fmttype": value.params.get("FMTTYPE"),
                "altrep": value.params.get("ALTREP"),
                "display": value.params.get("DISPLAY"),
            }
        )
        return cls(**params)

    def __init__(
        self,
        uri: str | None = None,
        b64data: str | None = None,
        fmttype: str | None = None,
        altrep: str | None = None,
        display: str | None = None,
    ):
        """Initialize a new Image according to RFC 7986.

        Args:
            uri (str | None): URI pointing to the image resource.
            b64data (str | None): Base64-encoded binary image data.
            fmttype (str | None): Media type of the image.
            altrep (str | None): Alternate representation link target.
            display (str | None): Intended display mode.

        Raises:
            ValueError: If both uri and b64data are provided or if neither is set.
        """
        if uri is not None and b64data is not None:
            raise ValueError("Image cannot have both URI and binary data (RFC 7986)")
        if uri is None and b64data is None:
            raise ValueError("Image must have either URI or binary data")
        self.uri = uri
        self.b64data = b64data
        self.fmttype = fmttype
        self.altrep = altrep
        self.display = display

    @property
    def data(self) -> bytes | None:
        """Return the decoded binary image data.

        Returns:
            bytes | None: The decoded binary data if available, otherwise None.
        """
        if self.b64data is None:
            return None
        return base64.b64decode(self.b64data)


__all__ = ["Image"]
