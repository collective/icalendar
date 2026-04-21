"""This module parses and generates contentlines as defined in RFC 5545
(iCalendar), but will probably work for other MIME types with similar syntax.
Eg. RFC 2426 (vCard)

It is stupid in the sense that it treats the content purely as strings. No type
conversion is attempted.
"""

from .content_line import Contentline, Contentlines
from .parameter import (
    Parameters,
    _dquote,
    _param_value,
    _q_join,
    _q_split,
    _rfc_6868_escape,
    _rfc_6868_unescape,
    _validate_param_value,
    dquote,
    param_value,
    q_join,
    q_split,
    rfc_6868_escape,
    rfc_6868_unescape,
    validate_param_value,
)
from .property import (
    _split_on_unescaped_comma,
    _split_on_unescaped_semicolon,
    _unescape_backslash,
    _unescape_list_or_string,
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
    _validate_token,
    escape_char,
    escape_string,
    foldline,
    unescape_char,
    unescape_string,
    validate_token,
)

__all__ = [
    "Contentline",
    "Contentlines",
    "Parameters",
    "_dquote",
    "_escape_char",
    "_escape_string",
    "_foldline",
    "_param_value",
    "_q_join",
    "_q_split",
    "_rfc_6868_escape",
    "_rfc_6868_unescape",
    "_split_on_unescaped_comma",
    "_split_on_unescaped_semicolon",
    "_unescape_backslash",
    "_unescape_char",
    "_unescape_list_or_string",
    "_unescape_string",
    "_validate_param_value",
    "_validate_token",
    "dquote",
    "escape_char",
    "escape_string",
    "foldline",
    "param_value",
    "q_join",
    "q_split",
    "rfc_6868_escape",
    "rfc_6868_unescape",
    "split_on_unescaped_comma",
    "split_on_unescaped_semicolon",
    "unescape_backslash",
    "unescape_char",
    "unescape_list_or_string",
    "unescape_string",
    "validate_param_value",
    "validate_token",
]
