"""Test that we get the right output under all conditions.

Run with:

    pytest .github/workflows/test_generate_matrix.py

"""

import pytest
from generate_matrix import generate_matrix

COUNT_ALL = 7
COUNT_MIN = 3


@pytest.mark.parametrize(
    ("arg_pr", "expected", "arg_ref"),
    [
        # push
        ("", COUNT_ALL, "refs/heads/main"),
        ("", COUNT_ALL, "refs/heads/7.x"),
        ("", COUNT_ALL, "refs/heads/6.x"),
        ("", COUNT_ALL, "refs/heads/5.x"),
        ("", COUNT_ALL, "refs/heads/release-1"),
        ("", COUNT_ALL, "refs/tags/v7.0.2"),
        ("", COUNT_MIN, "refs/heads/pr-branch"),
        # review
        ("changes_requested", 0, "refs/heads/main"),
        ("changes_requested", 0, "refs/heads/7.x"),
        ("changes_requested", 0, "refs/heads/6.x"),
        ("changes_requested", 0, "refs/heads/5.x"),
        ("changes_requested", 0, "refs/heads/release-2"),
        ("changes_requested", 0, "refs/tags/v7.0.2"),
        ("changes_requested", 0, "refs/heads/pr-branch"),
        ("approved", COUNT_ALL, "refs/heads/main"),
        ("approved", COUNT_ALL, "refs/heads/7.x"),
        ("approved", COUNT_ALL, "refs/heads/6.x"),
        ("approved", COUNT_ALL, "refs/heads/5.x"),
        ("approved", COUNT_ALL, "refs/heads/release-3"),
        ("approved", COUNT_ALL, "refs/tags/v7.0.2"),
        ("approved", COUNT_ALL, "refs/heads/pr-branch"),
    ],
)
def test_count_test_runs(arg_ref, arg_pr, expected):
    """Check which values we get."""
    matrix = generate_matrix(arg_ref, arg_pr)
    for case in matrix:
        print(f"- {case['test_name']}")
    assert len(matrix) == expected, f"Expected {expected} test runs, got {len(matrix)}"


@pytest.mark.parametrize(
    ("arg_pr", "arg_ref"),
    [
        # push
        ("", "refs/heads/main"),
        ("approved", "refs/heads/6.x"),
    ],
)
def test_pypy_is_first(arg_ref, arg_pr):
    """PyPy takes longest to run, so it should be triggered first.

    See https://github.com/collective/icalendar/pull/1239#discussion_r2868711107
    """
    matrix = generate_matrix(arg_ref, arg_pr)
    assert matrix[0]["test_name"] == "pypy3"
