"""Functions for manipulating strings and bytes."""

import re

from icalendar.compatibility import deprecate_for_version_8
from icalendar.parser_tools import DEFAULT_ENCODING, to_unicode


def _escape_char(text: str | bytes) -> str:
    r"""Format value according to iCalendar TEXT escaping rules.

    Escapes special characters in text values according to :rfc:`5545#section-3.3.11`
    rules.
    The order of replacements matters to avoid double-escaping.

    Parameters:
        text: The text to escape.

    Returns:
        The escaped text with special characters escaped.

    Note:
        The replacement order is critical:

        1. ``\N`` -> ``\n`` (normalize newlines to lowercase)
        2. ``\`` -> ``\\`` (escape backslashes)
        3. ``;`` -> ``\;`` (escape semicolons)
        4. ``,`` -> ``\,`` (escape commas)
        5. ``\r\n`` -> ``\n`` (normalize line endings)
        6. ``"\n"`` -> ``r"\n"`` (transform a newline character to a literal, or raw,
           newline character)
        7. ``"\r"`` -> ``r"\n"`` (transform a lone carriage return to a literal
           newline character)

        Steps 5 to 7 normalize ``\r\n``, ``\n``, or a lone ``\r`` to ``\n``.
        The line-ending normalization is an implementation convenience,
        not part of :rfc:`5545`, which only defines ``\n`` or ``\N`` for an
        intentional line break, and doesn't give an escape form for a lone ``\r``.
    """
    assert isinstance(text, (str, bytes))
    text = to_unicode(text)
    # NOTE: ORDER MATTERS!
    return (
        text.replace(r"\N", "\n")
        .replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\r\n", r"\n")
        .replace("\n", r"\n")
        .replace("\r", r"\n")
    )


escape_char = deprecate_for_version_8(_escape_char)
"""Format value according to iCalendar TEXT escaping rules.

.. deprecated:: 7.0.0
    Use the private :func:`_escape_char` internally. For external use,
    this function is deprecated. Please use alternative escaping methods
    or contact the maintainers.
"""


def _unescape_char(text: str | bytes) -> str | bytes | None:
    r"""Unescape iCalendar TEXT values.

    Reverses the escaping applied by :func:`_escape_char` according to
    :rfc:`5545#section-3.3.11` TEXT escaping rules.

    Parameters:
        text: The escaped text.

    Returns:
        The unescaped text, or ``None`` if ``text`` is neither ``str`` nor ``bytes``.

    Note:
        The replacement order is critical to avoid double-unescaping:

        1. ``\N`` -> ``\n`` (intermediate step)
        2. ``\r\n`` -> ``\n`` (normalize line endings)
        3. ``\n`` -> newline (unescape newlines)
        4. ``\,`` -> ``,`` (unescape commas)
        5. ``\;`` -> ``;`` (unescape semicolons)
        6. ``\\`` -> ``\`` (unescape backslashes last)
    """
    assert isinstance(text, (str, bytes))
    # NOTE: ORDER MATTERS!
    if isinstance(text, str):
        return (
            text.replace("\\N", "\\n")
            .replace("\r\n", "\n")
            .replace("\\n", "\n")
            .replace("\\,", ",")
            .replace("\\;", ";")
            .replace("\\\\", "\\")
        )
    if isinstance(text, bytes):
        return (
            text.replace(b"\\N", b"\\n")
            .replace(b"\r\n", b"\n")
            .replace(b"\\n", b"\n")
            .replace(b"\\,", b",")
            .replace(b"\\;", b";")
            .replace(b"\\\\", b"\\")
        )
    return None


unescape_char = deprecate_for_version_8(_unescape_char)
"""Unescape iCalendar TEXT values.

.. deprecated:: 7.0.0
    Use the private :func:`_unescape_char` internally. For external use,
    this function is deprecated. Please use alternative unescaping methods
    or contact the maintainers.
"""


def _foldline(line: str, limit: int = 75, fold_sep: str = "\r\n ") -> str:
    """Make a string folded as defined in RFC5545.

    Lines of text SHOULD NOT be longer than 75 octets, excluding the line
    break.  Long content lines SHOULD be split into a multiple line
    representations using a line "folding" technique.  That is, a long
    line can be split between any two characters by inserting a CRLF
    immediately followed by a single linear white-space character (i.e.,
    SPACE or HTAB).
    """
    assert isinstance(line, str)
    assert "\n" not in line

    folded_lines: list[str] = []
    current_chars: list[str] = []
    byte_count = 0
    for char in line:
        char_byte_len = len(char.encode(DEFAULT_ENCODING))
        if current_chars and byte_count + char_byte_len >= limit:
            # For compatibility with existing clients, avoid splitting escaped
            # values such as TEXT backslash escapes or RFC 6868 parameter
            # escapes across a folded line boundary. See issue #1501.
            if len(current_chars) > 1 and current_chars[-1] in r"\^":
                escaped_prefix = current_chars.pop()
                folded_lines.append("".join(current_chars))
                current_chars = [escaped_prefix]
                byte_count = len(escaped_prefix.encode(DEFAULT_ENCODING))
            else:
                folded_lines.append("".join(current_chars))
                current_chars = []
                byte_count = 0
        current_chars.append(char)
        byte_count += char_byte_len

    if current_chars:
        folded_lines.append("".join(current_chars))

    return fold_sep.join(folded_lines)


foldline = deprecate_for_version_8(_foldline)
"""Make a string folded as defined in RFC5545.

.. deprecated:: 7.0.0
    Use the private :func:`_foldline` internally.
"""


def _escape_string(val: str) -> str:
    r"""Escape backslash sequences to URL-encoded hex values.

    Converts backslash-escaped characters to their percent-encoded hex
    equivalents. This is used for parameter parsing to preserve escaped
    characters during processing.

    Parameters:
        val: The string with backslash escapes.

    Returns:
        The string with backslash escapes converted to percent encoding.

    Note:
        Conversions:

        - ``%`` -> ``%25``
        - ``\,`` -> ``%2C``
        - ``\:`` -> ``%3A``
        - ``\;`` -> ``%3B``
        - ``\\`` -> ``%5C``

        A literal ``%`` is escaped first so that percent sequences already in
        the value (e.g. ``%2C`` in a URI) are not confused with the markers
        introduced here. :func:`_unescape_string` reverses it.
    """
    # f'{i:02X}'
    return (
        val.replace("%", "%25")
        .replace(r"\,", "%2C")
        .replace(r"\:", "%3A")
        .replace(r"\;", "%3B")
        .replace(r"\\", "%5C")
    )


escape_string = deprecate_for_version_8(_escape_string)
"""Escape backslash sequences to URL-encoded hex values.

.. deprecated:: 7.0.0
    Use the private :func:`_escape_string` internally. For external use,
    this function is deprecated.
"""


def _unescape_string(val: str) -> str:
    r"""Unescape URL-encoded hex values to their original characters.

    Reverses :func:`_escape_string` by converting percent-encoded hex values
    back to their original characters. This is used for parameter parsing.

    Parameters:
        val: The string with percent-encoded values.

    Returns:
        The string with percent encoding converted to characters.

    Note:
        Conversions:

        - ``%2C`` -> ``,``
        - ``%3A`` -> ``:``
        - ``%3B`` -> ``;``
        - ``%5C`` -> ``\``
        - ``%25`` -> ``%``

        ``%25`` is restored last so a literal ``%`` that :func:`_escape_string`
        protected does not re-trigger the marker replacements above.
    """
    return (
        val.replace("%2C", ",")
        .replace("%3A", ":")
        .replace("%3B", ";")
        .replace("%5C", "\\")
        .replace("%25", "%")
    )


unescape_string = deprecate_for_version_8(_unescape_string)
"""Unescape URL-encoded hex values to their original characters.

.. deprecated:: 7.0.0
    Use the private :func:`_unescape_string` internally. For external use,
    this function is deprecated.
"""


# [\w-] because of the iCalendar RFC
# . because of the vCard RFC
NAME = re.compile(r"[\w.-]+")


def validate_token(name: str) -> None:
    r"""Validate that a name is a valid iCalendar token.

    Checks if the name matches the :rfc:`5545` token syntax using the NAME
    regex pattern (``[\w.-]+``).

    Parameters:
        name: The token name to validate.

    Raises:
        ValueError: If the name is not a valid token.
    """
    match = NAME.findall(name)
    if len(match) == 1 and name == match[0]:
        return
    raise ValueError(name)


__all__ = [
    "_escape_char",
    "_escape_string",
    "_foldline",
    "_unescape_char",
    "_unescape_string",
    "escape_char",
    "escape_string",
    "foldline",
    "unescape_char",
    "unescape_string",
    "validate_token",
]
