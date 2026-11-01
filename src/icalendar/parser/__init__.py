"""This module parses and generates contentlines as defined in RFC 5545
(iCalendar), but will probably work for other MIME types with similar syntax.
Eg. RFC 2426 (vCard)

It is stupid in the sense that it treats the content purely as strings. No type
conversion is attempted.
"""

from .content_line import Contentline, Contentlines
from .parameter import (
    Parameters,
    _rfc_6868_escape,
    _rfc_6868_unescape,
    dquote,
    param_value,
    q_join,
    q_split,
    validate_param_value,
)
from .property import (
    split_on_unescaped_comma,
    split_on_unescaped_semicolon,
    unescape_backslash,
    unescape_list_or_string,
)
from .string import (
    _escape_char,
    _escape_string,
    _foldline,
    _unescape_char,
    _unescape_string,
    validate_token,
)

__all__ = [
    "Contentline",
    "Contentlines",
    "Parameters",
    "_escape_char",
    "_escape_string",
    "_foldline",
    "_rfc_6868_escape",
    "_rfc_6868_unescape",
    "_unescape_char",
    "_unescape_string",
    "dquote",
    "param_value",
    "q_join",
    "q_split",
    "split_on_unescaped_comma",
    "split_on_unescaped_semicolon",
    "unescape_backslash",
    "unescape_list_or_string",
    "validate_param_value",
    "validate_token",
]
