"""This test tests all fuzzed calendars.

To add a new calendar test, echo the base64 calendar string into a file.

- The file is in src/icalendar/tests/calendars
- The file name contains "fuzz_testcase" and ends with ".ics"

Templace code to create a new test case:

.. code-block:: console

    echo "" | base64 -d > src/icalendar/tests/calendars/fuzz_testcase_.ics

"""

import pytest

import icalendar.cal.calendar
from icalendar.tests.fuzzed import fuzz_v1_calendar, is_expected_exception


def test_fuzz_v1(fuzz_v1_calendar_path):
    """Test a calendar."""
    calendar = fuzz_v1_calendar_path.read_bytes()
    print(repr(calendar))
    fuzz_v1_calendar(
        icalendar.cal.calendar.Calendar.from_ical,
        calendar,
        multiple=True,
        should_walk=True,
    )


def test_format_fuzz_log():
    import base64

    from icalendar.tests.fuzzed import format_fuzz_log

    content = "BEGIN:VCALENDAR\r\nEND:VCALENDAR"
    log = format_fuzz_log(
        icalendar.cal.calendar.Calendar.from_ical,
        multiple=False,
        should_walk=True,
        calendar_string=content,
    )
    assert log.startswith(
        "test_format_fuzz_log Calendar.from_ical multiple=False should_walk=True "
    )
    encoded = log.split()[-1]
    assert base64.b64decode(encoded).decode("utf-8") == content


@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        (ValueError("Expected a value"), True),
        (TypeError("Wrong date format"), True),
        (ValueError("an unknown problem"), False),
        (KeyError("Expected a value"), False),
        (AttributeError("Expected a value"), False),
    ],
)
def test_is_expected_exception(exception, expected):
    """The current check looks at the type and the message of the exception."""
    assert is_expected_exception(exception) is expected


def raise_error(error):
    """Return a from_ical function that raises the error."""

    def from_ical(calendar_string, multiple):
        raise error

    return from_ical


def test_fuzzer_ignores_expected_exception():
    """The fuzzer returns -1 for an exception that is expected."""
    from_ical = raise_error(ValueError("Expected a value"))
    assert fuzz_v1_calendar(from_ical, "", multiple=False, should_walk=False) == -1


@pytest.mark.parametrize(
    "error",
    [ValueError("an unknown problem"), KeyError("Expected a value")],
)
def test_fuzzer_raises_unexpected_exception(error):
    """The fuzzer raises an exception that no predicate matches."""
    from_ical = raise_error(error)
    with pytest.raises(type(error)):
        fuzz_v1_calendar(from_ical, "", multiple=False, should_walk=False)
