"""Test the predicates that decide which exceptions the fuzzer ignores.

See https://github.com/collective/icalendar/issues/1759
"""

import pytest

from icalendar.tests.fuzzed import (
    Predicate,
    fuzz_v1_calendar,
    is_expected_exception,
)

always = Predicate(lambda _: True)
never = Predicate(lambda _: False)


@pytest.mark.parametrize(
    ("predicate", "expected"),
    [
        (always, True),
        (never, False),
        (always & always, True),
        (always & never, False),
        (never & always, False),
        (always | never, True),
        (never | always, True),
        (never | never, False),
        (~always, False),
        (~never, True),
        (~(always & never), True),
        (always & (lambda _: False), False),
        (never | (lambda _: True), True),
    ],
)
def test_combine_predicates(predicate, expected):
    """Predicates can be combined with &, | and ~."""
    assert predicate(ValueError()) is expected


@pytest.mark.parametrize(
    "predicate", [always & never, always | never, ~always, always & (lambda _: True)]
)
def test_combined_predicate_is_a_predicate(predicate):
    """Combining predicates returns a predicate, so we can combine it again."""
    assert isinstance(predicate, Predicate)


def test_predicate_gets_the_exception():
    """The function of the predicate is called with the exception."""
    error = ValueError("test")
    seen = []
    Predicate(seen.append)(error)
    assert seen == [error]


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
