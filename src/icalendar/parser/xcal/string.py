"""Common parsing functions based on string."""

import math
import re


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


_INVALID_XML_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ufffe\uffff]")
"""Match the characters that XML 1.0 does not allow in a document.

The ``Char`` production in section 2.2 of XML 1.0 allows only
``#x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]``.
This pattern matches the characters outside of it that a Python :class:`str`
can contain, apart from surrogates:

- the C0 control characters ``#x0`` to ``#x1F``, except tab, line feed and
  carriage return, and
- the noncharacters ``#xFFFE`` and ``#xFFFF``.

Lone surrogates ``#xD800`` to ``#xDFFF`` are also outside ``Char``, but are not
matched here. They cannot be encoded as UTF-8, and ``to_ical()`` rejects them.

.. seealso::

    `XML 1.0, section 2.2 Characters <https://www.w3.org/TR/REC-xml/#charsets>`_
"""


def _to_valid_xml_string(string: str) -> str:
    """Remove all characters that are not valid XML characters.

    Returns:

        A string with all characters that are not valid XML characters removed.

    .. seealso::

        `XML Character Range <https://www.w3.org/TR/REC-xml/#charsets>`_,
        `~icalendar.prop.text._strip_unsafe_text_chars`,
        `Issue 1888 <https://github.com/collective/icalendar/issues/1888>`_,
    """
    return _INVALID_XML_CHARACTERS.sub("", string)


__all__ = ["_to_valid_xml_string", "string_to_xsd_float", "xsd_float_to_string"]
