"""Tests for parser_tools module."""

import pytest

from icalendar.parser_tools import from_unicode, to_unicode


def test_from_unicode_raises_type_error_for_invalid_input():
    """from_unicode should raise TypeError for non-str/bytes input."""
    with pytest.raises(TypeError, match="Expected str or bytes"):
        from_unicode(123)


def test_to_unicode_raises_type_error_for_invalid_input():
    """to_unicode should raise TypeError for non-str/bytes input."""
    with pytest.raises(TypeError, match="Expected str or bytes"):
        to_unicode(123)
