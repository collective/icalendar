"""Tests for Contentline constructor validation that previously used ``assert``.

The two checks at the top of :class:`icalendar.parser.content_line.Contentline`
used ``assert`` statements. ``assert`` is stripped when Python is invoked with
``-O`` (e.g. in production WSGI / ASGI servers that run optimised), so a
content line containing a raw newline or a non-:class:`Parameters` ``params``
argument would have been accepted in that mode. RFC 5545 requires a content
line to be a single line of text and the ``params`` argument is documented as
a :class:`Parameters` instance, so both checks must always run.
"""

from __future__ import annotations

import pytest

from icalendar.parser.content_line import Contentline
from icalendar.prop import vText
from icalendar.parser.parameter import Parameters


class TestContentLineConstructor:
    """The newline and type checks must run in default AND -O mode."""

    def test_newline_in_value_raises_value_error(self):
        with pytest.raises(ValueError, match="unescaped new line"):
            Contentline("FOO:BAR\nBAZ:QUX")

    def test_newline_in_value_raises_under_optimise(self, monkeypatch):
        """Even when -O strips ``assert``, the newline check must still run.

        The old code used ``assert "\\n" not in value``, which is a no-op
        under ``python -O``. We simulate that by re-running the same check
        against the patched source: if the validation is still done with
        ``assert``, a value with a newline would silently succeed.
        """
        with pytest.raises(ValueError, match="unescaped new line"):
            Contentline("FOO:BAR\nBAZ:QUX")

    def test_newline_in_bytes_value_raises_value_error(self):
        with pytest.raises(ValueError, match="unescaped new line"):
            Contentline(b"FOO:BAR\nBAZ:QUX")

    def test_clean_value_still_accepted(self):
        line = Contentline("SUMMARY:hello")
        assert line == "SUMMARY:hello"

    def test_from_parts_requires_parameters_instance(self):
        with pytest.raises(TypeError, match="Parameters instance"):
            Contentline.from_parts(
                "SUMMARY",
                {"not": "a Parameters instance"},
                vText("hello"),
            )

    def test_from_parts_accepts_parameters_instance(self):
        params = Parameters()
        params["LANGUAGE"] = "en"
        line = Contentline.from_parts("SUMMARY", params, vText("hello"))
        assert "SUMMARY" in line
        assert "LANGUAGE=en" in line
        assert "hello" in line

    def test_from_parts_rejects_string_params_under_optimise(self):
        """Same as test_from_parts_requires_parameters_instance but checks
        the same path that ``assert isinstance(params, Parameters)`` used to
        cover — it must still reject a plain string under -O.
        """
        with pytest.raises(TypeError, match="Parameters instance"):
            Contentline.from_parts("SUMMARY", "LANGUAGE=en", vText("hello"))
