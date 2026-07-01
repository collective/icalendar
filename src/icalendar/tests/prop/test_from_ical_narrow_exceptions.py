"""Narrow-exception behavior for ``from_ical`` on the simple prop types.

The ``from_ical`` methods used to wrap their work in a bare
``except Exception`` and re-raise a more informative ``ValueError``.
That is a code-smell: a bare except swallows everything including
``KeyboardInterrupt`` and ``MemoryError``, and hides bugs that have
nothing to do with the parse.

Each prop now catches only the exception types that the try-block can
actually raise, and re-raises with the same wrapped ``ValueError``
message that callers downstream (and the existing test suite) depend
on. These tests pin the narrowed behavior:

* valid input still parses to the right value
* malformed input still raises ``ValueError`` (so the existing
  ``pytest.raises(ValueError)`` tests keep working)
* invalid input (None, list, dict) raises a sensible error too — the
  old ``except Exception`` hid the precise type, but a narrowed except
  that covers ``TypeError`` and ``AttributeError`` (for ``None.split``,
  ``None.upper``, etc.) keeps the user-facing behavior consistent.
"""
import pytest

from icalendar.prop import vBoolean, vUri, vInt, vFloat, vGeo
from icalendar.prop.dt.date import vDate
from icalendar.prop.dt.datetime import vDatetime
from icalendar.prop.dt.period import vPeriod
from icalendar.prop.dt.time import vTime


class TestNarrowExceptionTypes:
    """The narrowed ``except`` clauses cover the same input failures as
    the old ``except Exception``, with the same wrapped ``ValueError``."""

    # --- bad input still raises ValueError (the pre-existing behavior) ---

    def test_vInt_bad_string_raises_value_error(self):
        with pytest.raises(ValueError):
            vInt.from_ical("not an int")

    def test_vFloat_bad_string_raises_value_error(self):
        with pytest.raises(ValueError):
            vFloat.from_ical("not a float")

    def test_vBoolean_bad_string_raises_value_error(self):
        with pytest.raises(ValueError):
            vBoolean.from_ical("ture")

    def test_vDate_short_string_raises_value_error(self):
        with pytest.raises(ValueError):
            vDate.from_ical("200102")

    def test_vTime_bad_hour_raises_value_error(self):
        with pytest.raises(ValueError):
            vTime.from_ical("263000")

    def test_vDatetime_bad_char_raises_value_error(self):
        with pytest.raises(ValueError):
            vDatetime.from_ical("20010101T000000A")

    def test_vPeriod_no_slash_raises_value_error(self):
        with pytest.raises(ValueError):
            vPeriod.from_ical("20010101T000000")

    def test_vGeo_from_ical_no_semicolon_raises_value_error(self):
        with pytest.raises(ValueError):
            vGeo.from_ical("1.0")

    # --- valid input still round-trips ---

    def test_vInt_valid(self):
        assert vInt.from_ical("42") == 42

    def test_vFloat_valid(self):
        assert vFloat.from_ical("42.0") == 42.0

    def test_vBoolean_valid(self):
        assert vBoolean.from_ical("TRUE") is True
        assert vBoolean.from_ical("FALSE") is False

    def test_vDate_valid(self):
        from datetime import date
        assert vDate.from_ical("20010102") == date(2001, 1, 2)

    def test_vTime_valid(self):
        from datetime import time
        assert vTime.from_ical("123000") == time(12, 30)

    def test_vDatetime_valid(self):
        from datetime import datetime
        assert vDatetime.from_ical("20000101T120000") == datetime(2000, 1, 1, 12, 0)

    def test_vGeo_from_ical_valid(self):
        assert vGeo.from_ical("1.0;2.0") == (1.0, 2.0)

    def test_vUri_valid(self):
        assert vUri.from_ical("http://example.com") == "http://example.com"

    # --- None / non-string still surface a clear error ---

    def test_vInt_none_raises_type_error(self):
        # ``int(None)`` raises TypeError, which the narrowed
        # ``except (ValueError, TypeError)`` lets propagate as a
        # clear type error rather than the wrapped ValueError.
        with pytest.raises(TypeError):
            vInt.from_ical(None)

    def test_vFloat_none_raises_type_error(self):
        with pytest.raises(TypeError):
            vFloat.from_ical(None)

    def test_vBoolean_none_raises_value_error(self):
        # ``None.upper()`` raises AttributeError, which the narrowed
        # ``except (KeyError, ValueError, TypeError, AttributeError)``
        # catches and re-wraps as a clearer ValueError.
        with pytest.raises(ValueError):
            vBoolean.from_ical(None)

    def test_vDate_none_raises_value_error(self):
        # ``None[4:6]`` raises TypeError; the narrowed
        # ``except (ValueError, TypeError, IndexError, AttributeError)``
        # wraps it as a clear ValueError.
        with pytest.raises(ValueError):
            vDate.from_ical(None)

    def test_vTime_none_raises_value_error(self):
        with pytest.raises(ValueError):
            vTime.from_ical(None)

    def test_vDatetime_none_raises_value_error(self):
        with pytest.raises(ValueError):
            vDatetime.from_ical(None)

    def test_vPeriod_none_raises_value_error(self):
        # ``None.split("/")`` raises AttributeError; the narrowed
        # except clause catches it and wraps as ValueError.
        with pytest.raises(ValueError):
            vPeriod.from_ical(None)

    def test_vGeo_from_ical_none_raises_value_error(self):
        with pytest.raises(ValueError):
            vGeo.from_ical(None)

    # --- bytes input (where supported) still works ---

    def test_vUri_bytes_works(self):
        assert vUri.from_ical(b"http://x") == "http://x"

    def test_vDatetime_bytes_works(self):
        from datetime import datetime
        assert vDatetime.from_ical(b"20240115T100000") == datetime(2024, 1, 15, 10, 0)

    def test_vTime_bytes_works(self):
        from datetime import time
        assert vTime.from_ical(b"123000") == time(12, 30)
