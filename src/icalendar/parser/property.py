"""Tools for parsing properties."""

import re
import warnings

from icalendar.parser.string import _unescape_string


def _unescape_list_or_string(val: str | list[str]) -> str | list[str]:
    """Unescape a value that may be a string or list of strings.

    Applies :func:`_unescape_string` to the value. If the value is a list,
    unescapes each element.

    Parameters:
        val: A string or list of strings to unescape.

    Returns:
        The unescaped values.
    """
    if isinstance(val, list):
        return [_unescape_string(s) for s in val]
    return _unescape_string(val)


def unescape_list_or_string(val: str | list[str]) -> str | list[str]:
    """Unescape a value that may be a string or list of strings.

    .. deprecated:: 7.0.0
        Use the private :func:`_unescape_list_or_string` internally. For
        external use, this function is deprecated. Please contact the
        maintainers if you rely on this function.
    """
    warnings.warn(
        "unescape_list_or_string is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _unescape_list_or_string(val)


_unescape_backslash_regex = re.compile(r"\\([\\,;:nN])")


def _unescape_backslash(val: str):
    r"""Unescape backslash sequences in iCalendar text.

    Unlike :py:meth:`_unescape_string`, this only handles actual backslash escapes
    per :rfc:`5545`, not URL encoding. This preserves URL-encoded values
    like ``%3A`` in URLs.

    Processes backslash escape sequences in a single pass using regex matching.
    """
    return _unescape_backslash_regex.sub(
        lambda m: "\n" if m.group(1) in "nN" else m.group(1), val
    )


def unescape_backslash(val: str):
    r"""Unescape backslash sequences in iCalendar text.

    .. deprecated:: 7.0.0
        Use the private :func:`_unescape_backslash` internally. For external
        use, this function is deprecated. Please contact the maintainers if you
        rely on this function.
    """
    warnings.warn(
        "unescape_backslash is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _unescape_backslash(val)


def _split_on_unescaped_comma(text: str) -> list[str]:
    r"""Split text on unescaped commas and unescape each part.

    Splits only on commas not preceded by backslash.
    After splitting, unescapes backslash sequences in each part.

    Parameters:
        text: Text with potential escaped commas (e.g., "foo\\, bar,baz")

    Returns:
        List of unescaped category strings

    Examples:
        .. code-block:: pycon

            >>> from icalendar.parser.property import _split_on_unescaped_comma
            >>> _split_on_unescaped_comma(r"foo\, bar,baz")
            ['foo, bar', 'baz']
            >>> _split_on_unescaped_comma("a,b,c")
            ['a', 'b', 'c']
            >>> _split_on_unescaped_comma(r"a\,b\,c")
            ['a,b,c']
            >>> _split_on_unescaped_comma(r"Work,Personal\,Urgent")
            ['Work', 'Personal,Urgent']
    """
    if not text:
        return [""]

    result = []
    current = []
    i = 0

    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            # Escaped character - keep both backslash and next char
            current.append(text[i])
            current.append(text[i + 1])
            i += 2
        elif text[i] == ",":
            # Unescaped comma - split point
            result.append(_unescape_backslash("".join(current)))
            current = []
            i += 1
        else:
            current.append(text[i])
            i += 1

    # Add final part
    result.append(_unescape_backslash("".join(current)))

    return result


def split_on_unescaped_comma(text: str) -> list[str]:
    r"""Split text on unescaped commas and unescape each part.

    .. deprecated:: 7.0.0
        Use the private :func:`_split_on_unescaped_comma` internally. For
        external use, this function is deprecated. Please contact the
        maintainers if you rely on this function.
    """
    warnings.warn(
        "split_on_unescaped_comma is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _split_on_unescaped_comma(text)


def _split_on_unescaped_semicolon(text: str) -> list[str]:
    r"""Split text on unescaped semicolons and unescape each part.

    Splits only on semicolons not preceded by a backslash.
    After splitting, unescapes backslash sequences in each part.
    Used by vCard structured properties (ADR, N, ORG) per :rfc:`6350`.

    Parameters:
        text: Text with potential escaped semicolons (e.g., "field1\\;with;field2")

    Returns:
        List of unescaped field strings

    Examples:
        .. code-block:: pycon

            >>> from icalendar.parser.property import _split_on_unescaped_semicolon
            >>> _split_on_unescaped_semicolon(r"field1\;with;field2")
            ['field1;with', 'field2']
            >>> _split_on_unescaped_semicolon("a;b;c")
            ['a', 'b', 'c']
            >>> _split_on_unescaped_semicolon(r"a\;b\;c")
            ['a;b;c']
            >>> _split_on_unescaped_semicolon(r"PO Box 123\;Suite 200;City")
            ['PO Box 123;Suite 200', 'City']
    """
    if not text:
        return [""]

    result = []
    current = []
    i = 0

    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text):
            # Escaped character - keep both backslash and next char
            current.append(text[i])
            current.append(text[i + 1])
            i += 2
        elif text[i] == ";":
            # Unescaped semicolon - split point
            result.append(_unescape_backslash("".join(current)))
            current = []
            i += 1
        else:
            current.append(text[i])
            i += 1

    # Add final part
    result.append(_unescape_backslash("".join(current)))

    return result


def split_on_unescaped_semicolon(text: str) -> list[str]:
    r"""Split text on unescaped semicolons and unescape each part.

    .. deprecated:: 7.0.0
        Use the private :func:`_split_on_unescaped_semicolon` internally. For
        external use, this function is deprecated. Please contact the
        maintainers if you rely on this function.
    """
    warnings.warn(
        "split_on_unescaped_semicolon is deprecated and will be removed in a future version. "
        "If you are using this function externally, please contact the maintainers.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _split_on_unescaped_semicolon(text)


__all__ = [
    "_split_on_unescaped_comma",
    "_split_on_unescaped_semicolon",
    "_unescape_backslash",
    "_unescape_list_or_string",
    "split_on_unescaped_comma",
    "split_on_unescaped_semicolon",
    "unescape_backslash",
    "unescape_list_or_string",
]
