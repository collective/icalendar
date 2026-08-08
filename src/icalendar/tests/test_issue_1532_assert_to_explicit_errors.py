"""Test for GitHub issue #1532:

Four ``assert`` guards in the parsing pipeline were silently stripped under
``python -O``, allowing invalid content lines and wrong-type inputs to pass
through unchecked. The guards are now unconditional ``if``/``raise`` checks.

See :class:`~icalendar.parser.content_line.Contentline`,
:func:`~icalendar.parser.string._escape_char`,
:func:`~icalendar.parser.string._unescape_char`, and
:func:`~icalendar.parser.string._foldline`.
"""

import pytest

from icalendar.parser import Contentline, _foldline
from icalendar.parser.string import _escape_char, _unescape_char


@pytest.mark.parametrize(
    ("func", "value", "exc"),
    [
        (Contentline, "foo\nbar", ValueError),
        (_escape_char, 123, TypeError),
        (_unescape_char, 123, TypeError),
        (_foldline, b"bytes input", TypeError),
        (_foldline, "foo\nbar", ValueError),
    ],
)
def test_guards_raise_without_assert(func, value, exc):
    """Each guard raises the right exception regardless of the -O flag."""
    with pytest.raises(exc):
        func(value)
