"""Test that we get the right output under all conditions.

Run with:

    pytest .github/workflows/test_generate_matrix.py

"""

import pytest
from generate_matrix import generate_matrix

CASES_ALL = {"3.10", "3.11", "3.12", "3.13", "3.14", "3.10 (nopytz)", "pypy3"}
CASES_MIN = {"3.10", "3.14", "3.10 (nopytz)"}
CASES_0 = set()


@pytest.fixture(
    params=[
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
def cases(request):
    """All test cases."""
    return request.param


@pytest.fixture
def arg_pr(cases):
    """The pr event name."""
    return cases[0]


@pytest.fixture
def arg_ref(cases):
    """The branch or tag reference."""
    return cases[2]


@pytest.fixture
def expected(cases):
    """All expected case names."""
    return cases[1]


@pytest.fixture
def matrix(arg_ref, arg_pr):
    """The generated test matrix."""
    matrix = generate_matrix(arg_ref, arg_pr)
    print("Cases:")
    for case in sorted(matrix["include"], key=lambda case: case["test_name"]):
        print(f"- running\t{case['test_name']}")
    for case in sorted(matrix["skipped"]):
        print(f"- skipped\t{case}")
    return matrix


@pytest.fixture
def skipped_names(matrix):
    """All skipped test cases."""
    return set(matrix["skipped"])


@pytest.fixture
def running_names(matrix):
    """All running test cases"""
    return {case["test_name"] for case in matrix["include"] if not case["skip"]}


def test_count_test_runs(running_names, expected):
    """Check which values we get."""
    assert running_names == expected, (
        f"Expected {len(expected)} test runs, got {len(running_names)}"
    )


def test_running_is_not_skipped(running_names, skipped_names):
    """Running means not skipped."""
    assert running_names.isdisjoint(skipped_names)


def test_all_cases_are_always_included(running_names, skipped_names, matrix):
    """The matirx always needs to be complete or we might wait for required checks."""
    assert running_names | skipped_names == CASES_ALL
    all_in_matrix = {case["test_name"] for case in matrix["include"]}
    assert all_in_matrix == CASES_ALL


@pytest.mark.parametrize(
    "attribute",
    [
        "test_name",
        "python_version",
        "skip",
        "install_command",
        "test_command",
    ],
)
def test_parameters_are_present(matrix, attribute):
    for case in matrix["include"]:
        assert attribute in case, f"Missing {attribute} in {case}"


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
    result = generate_matrix(arg_ref, arg_pr)
    assert result["include"][0]["test_name"] == "pypy3"
