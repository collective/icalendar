"""Issue #1532: parser guards must raise even under python -O.

``assert`` is stripped by ``-O``, so newline and type guards in the parsing
pipeline must use explicit ``if`` / ``raise`` checks.
"""

from __future__ import annotations

import pytest

from icalendar.parser.content_line import Contentline
from icalendar.parser.string import _escape_char, _foldline, _unescape_char


def test_contentline_rejects_embedded_newline():
    with pytest.raises(ValueError, match="new line"):
        Contentline("SUMMARY:Test\nINJECTED:Bad")


def test_foldline_rejects_embedded_newline():
    with pytest.raises(ValueError, match="new line"):
        _foldline("SUMMARY:Test\nINJECTED:Bad")


def test_foldline_rejects_non_str():
    with pytest.raises(TypeError, match="str"):
        _foldline(b"not-a-str")  # type: ignore[arg-type]


def test_escape_char_rejects_bad_type():
    with pytest.raises(TypeError, match="str or bytes"):
        _escape_char(123)  # type: ignore[arg-type]


def test_unescape_char_rejects_bad_type():
    with pytest.raises(TypeError, match="str or bytes"):
        _unescape_char(123)  # type: ignore[arg-type]
