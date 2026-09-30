"""Common parsing functions based on string."""

import math


def string_to_xsd_float(xsd_float: str) -> float:
    """Convert an xsd:float to a :class:`float`.

    Returns:
        The parsed float.

    Raises:
        ValueError: if the input is not an xsd:float
        TypeError: if the input is not :class:`str`
    """
    if not isinstance(xsd_float, str):
        raise TypeError("Expected xsd:float. Got None.")
    try:
        return float(xsd_float)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Expected xsd:float. Got {xsd_float!r}.") from e


def xsd_float_to_string(f: float) -> str:
    """Convert a :class:`float` to an xsd:float."""
    if math.isnan(f):
        return "NaN"
    if math.isfinite(f):
        return str(f)
    if f > 0:
        return "INF"
    return "-INF"


__all__ = [
    "string_to_xsd_float",
    "xsd_float_to_string",
]
