"""Test that we get the right output under all conditions.

Run with:

    pytest .github/workflows/test_generate_matrix.py

"""

import pytest
from generate_matrix import generate_matrix

CASES_ALL = {"3.10", "3.11", "3.12", "3.13", "3.14", "3.10 (nopytz)", "pypy3"}
CASES_MIN = {"3.10", "3.14", "3.10 (nopytz)"}
CASES_0 = set()


@pytest.mark.parametrize(
    ("arg_pr", "expected", "arg_ref"),
    [
        # push
        ("", CASES_ALL, "refs/heads/main"),
        ("", CASES_ALL, "refs/heads/7.x"),
        ("", CASES_ALL, "refs/heads/6.x"),
        ("", CASES_ALL, "refs/heads/5.x"),
        ("", CASES_ALL, "refs/heads/release-1"),
        ("", CASES_ALL, "refs/tags/v7.0.2"),
        ("", CASES_MIN, "refs/heads/pr-branch"),
        # review
        ("changes_requested", CASES_0, "refs/heads/main"),
        ("changes_requested", CASES_0, "refs/heads/7.x"),
        ("changes_requested", CASES_0, "refs/heads/6.x"),
        ("changes_requested", CASES_0, "refs/heads/5.x"),
        ("changes_requested", CASES_0, "refs/heads/release-2"),
        ("changes_requested", CASES_0, "refs/tags/v7.0.2"),
        ("changes_requested", CASES_0, "refs/heads/pr-branch"),
        ("approved", CASES_ALL, "refs/heads/main"),
        ("approved", CASES_ALL, "refs/heads/7.x"),
        ("approved", CASES_ALL, "refs/heads/6.x"),
        ("approved", CASES_ALL, "refs/heads/5.x"),
        ("approved", CASES_ALL, "refs/heads/release-3"),
        ("approved", CASES_ALL, "refs/tags/v7.0.2"),
        ("approved", CASES_ALL, "refs/heads/pr-branch"),
    ],
)
def test_count_test_runs(arg_ref, arg_pr, expected):
    """Check which values we get."""
    matrix = generate_matrix(arg_ref, arg_pr)
    print("Cases:")
    for case in sorted(matrix, key=lambda case: (case["skip"], case["test_name"])):
        print(f"- {case['skip']}\t{case['test_name']}")
    running = {case["test_name"] for case in matrix if not case["skip"]}
    assert running == expected, (
        f"Expected {len(expected)} test runs, got {len(running)}"
    )


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
