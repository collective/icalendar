"""Typing tests.

Run these tests with

    make test-types

Valid types in this directory are enforced.
"""


def test_wrong_type():
    """If this test is commented in, you can see an error.

    error: Type "Literal[1]" is not assignable to declared type "str"
    "Literal[1]" is not assignable to "str" (reportAssignmentType)
    """
    # a = 1
    # sequence: str = a # pyright: ignore[reportUnusedVariable]
