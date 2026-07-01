"""Narrow-exception behavior for ``from_ical`` on the recurrence / UTC offset /
Contentlines.parser paths that the related prop-narrowing PR does not cover.

The ``from_ical`` methods on ``vFrequency``, ``vWeekday``, ``vRecur``,
``vUTCOffset``, and ``Contentlines.from_ical`` used to wrap their body in
``except Exception`` and re-raise a ``ValueError``. The related prop-narrowing
PR narrows the except lists in the simple types (vInt, vFloat, vBoolean,
vDate, vTime, vDatetime, vUri, vGeo, vPeriod); this test covers the
recurrence / UTC offset / parser modules that PR leaves out.

Each test below covers one of the narrowed except lists and confirms both
the happy path (legitimate input still parses) and the unhappy path
(malformed input now raises the specific exception type that the narrowed
list catches, plus the wrap-into-ValueError behaviour the call site relies
on for user-facing error messages).
"""
import pytest
from datetime import timedelta

from icalendar.prop import vFrequency, vWeekday, vRecur, vUTCOffset
from icalendar.parser.content_line import Contentlines


class TestFrequencyNarrowExceptions:
    """``vFrequency.from_ical`` now catches only ``ValueError`` + ``AttributeError``."""

    def test_valid_frequency_parses(self):
        assert vFrequency.from_ical("DAILY") == "DAILY"
        assert vFrequency.from_ical("monthly") == "MONTHLY"

    def test_int_input_raises_value_error(self):
        # ``int.upper()`` raises AttributeError, which the narrowed except
        # wraps into ValueError. The pre-fix code raised ValueError via a
        # bare ``except Exception``; the post-fix code preserves that contract
        # by including AttributeError in the narrowed list.
        with pytest.raises(ValueError):
            vFrequency.from_ical(234)

    def test_none_input_raises_value_error(self):
        with pytest.raises(ValueError):
            vFrequency.from_ical(None)


class TestWeekdayNarrowExceptions:
    """``vWeekday.from_ical`` now catches only ``ValueError`` + ``AttributeError``."""

    def test_valid_weekday_parses(self):
        assert vWeekday.from_ical("MO") == "MO"
        assert vWeekday.from_ical("fr") == "FR"

    def test_non_string_input_raises_value_error(self):
        with pytest.raises(ValueError):
            vWeekday.from_ical(42)

    def test_none_input_raises_value_error(self):
        with pytest.raises(ValueError):
            vWeekday.from_ical(None)


class TestRecurNarrowExceptions:
    """``vRecur.from_ical`` now catches ``TypeError`` + ``AttributeError``
    in the outer handler (the inner ``ValueError`` is re-raised unchanged)."""

    def test_valid_recur_parses(self):
        rule = vRecur.from_ical("FREQ=DAILY;COUNT=5")
        assert rule == {"FREQ": ["DAILY"], "COUNT": [5]}

    def test_malformed_recur_raises_value_error(self):
        # Malformed pair: INTERVAL=abc triggers the int() ValueError path
        # inside the rule parser, which is re-raised as ValueError.
        with pytest.raises(ValueError):
            vRecur.from_ical("FREQ=DAILY;INTERVAL=abc")

    def test_non_string_recur_raises_value_error(self):
        with pytest.raises(ValueError):
            vRecur.from_ical(123)

    def test_none_recur_raises_value_error(self):
        with pytest.raises(ValueError):
            vRecur.from_ical(None)


class TestUTCOffsetNarrowExceptions:
    """``vUTCOffset.from_ical`` now catches ``ValueError``, ``TypeError``,
    and ``IndexError`` (int() raises ValueError/IndexError; slicing on
    non-string types raises TypeError)."""

    def test_valid_offset_parses(self):
        offset = vUTCOffset.from_ical("+0200")
        assert offset == timedelta(hours=2)

    def test_malformed_offset_raises_value_error(self):
        with pytest.raises(ValueError):
            vUTCOffset.from_ical("not a time")

    def test_too_short_offset_raises_value_error(self):
        # Slicing past the end raises IndexError, which is now in the except
        # list and gets wrapped into ValueError.
        with pytest.raises(ValueError):
            vUTCOffset.from_ical("+0")

    def test_non_string_offset_raises_value_error(self):
        with pytest.raises(ValueError):
            vUTCOffset.from_ical(12345)


class TestContentlinesNarrowExceptions:
    """``Contentlines.from_ical`` now catches only ``ValueError`` and
    ``TypeError`` (to_unicode normalizes the input first, so AttributeError
    is no longer reachable on the post-to_unicode body)."""

    def test_valid_string_parses(self):
        lines = Contentlines.from_ical("BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")
        assert len(lines) > 0

    def test_non_string_input_raises_value_error(self):
        # to_unicode raises a non-ValueError/TypeError (e.g. AttributeError)
        # for some inputs, but ValueError is what callers expect to catch;
        # check that the wrapping is at least a ValueError for inputs the
        # function used to accept.
        with pytest.raises(ValueError):
            Contentlines.from_ical(123)

    def test_none_input_raises_value_error(self):
        with pytest.raises(ValueError):
            Contentlines.from_ical(None)
