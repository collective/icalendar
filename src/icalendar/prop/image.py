"""This contains the IMAGE property from :rfc:`7986`."""

from __future__ import annotations

import base64

from icalendar.prop import vBinary, vText, vUri


class Image:
    """An image as URI or BINARY according to :rfc:`7986`."""

    @classmethod
    def from_property_value(cls, value: vUri | vBinary | vText):
        """Create an Image from a property value."""
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
        self.uri = uri
        self.b64data = b64data
        self.fmttype = fmttype
        self.altrep = altrep
        self.display = display

    @property
    def data(self) -> bytes | None:
        """Return the binary data, if available."""
        if self.b64data is None:
            return None
        return base64.b64decode(self.b64data)


__all__ = ["Image"]
