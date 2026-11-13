"""Test the predicates that decide which exceptions the fuzzer ignores.

See https://github.com/PyCalendar/icalendar/issues/1759
"""

import pytest

from icalendar.tests.fuzzed import Predicate

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
        (never & never, False),
        (always | always, True),
        (always | never, True),
        (never | always, True),
        (never | never, False),
        (~always, False),
        (~never, True),
        (~(always & never), True),
        (always & (lambda _: True), True),
        (always & (lambda _: False), False),
        (never & (lambda _: True), False),
        (never & (lambda _: False), False),
        (always | (lambda _: True), True),
        (always | (lambda _: False), True),
        (never | (lambda _: True), True),
        (never | (lambda _: False), False),
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
    """The function of the predicate is called with the same exception."""
    error = ValueError("test")
    seen = []
    Predicate(seen.append)(error)
    assert len(seen) == 1
    assert seen[0] is error
