#!/usr/bin/env python3
"""Generate the test matrix.

Parameters:
    0: The branch or tag that triggered the workflow
    1: The state of the pull request

Documentation:
- for python versions
  https://github.com/actions/setup-python/tree/v6/?tab=readme-ov-file#basic-usage
- for pull request approval
  https://stackoverflow.com/a/70441157/1320237

"""

import json
import re
import sys

#
# Configuration
#

PYTHON_MINOR_VERSION_MIN = 10
# Update this when a new Python minor version is released
PYTHON_MINOR_VERSION_MAX = 14


def generate_matrix(git_ref, review):
    """Generate a matrix of test runs.

    Parameters:
        arg_ref: The branch or tag that triggered the workflow
        arg_pr: The state of the pull request
    """
    #
    # Analyze the reference
    #
    runs_on_main = git_ref == "refs/heads/main"
    runs_on_stable = bool(re.match(r"refs/heads/\d+\.x", git_ref))
    runs_on_tag = git_ref.startswith("refs/tags/v")

    #
    # Analyze the trigger
    #

    # Analyze the review that triggered the workflow
    review_submitted = review != ""
    review_approved = review == "approved"

    # Which push to a branch or tag triggered the workflow
    # The trigger is either a push or a review, never both
    triggered_by_push_to_main = runs_on_main and not review_submitted
    triggered_by_push_to_stable = runs_on_stable and not review_submitted
    triggered_by_push_to_tag = runs_on_tag and not review_submitted

    run_all_jobs = (
        triggered_by_push_to_tag
        or triggered_by_push_to_main
        or triggered_by_push_to_stable
        or review_approved
    )

    run_no_jobs = review_submitted and not review_approved

    #
    # Debug conditions
    #
    for k, v in sorted(locals().items()):
        if isinstance(v, (bool, str, int)) and not k.startswith("_"):
            print(f"{k} = {v!r}")  # noqa: T201

    #
    # Create matrix
    #
    matrix: list[dict[str, str]] = []

    #
    # minimal set of jobs
    #
    if not run_no_jobs:
        # RULE: always test the lowest allowed version
        matrix.append(
            {"tox_env": "py", "python_version": f"3.{PYTHON_MINOR_VERSION_MIN}"}
        )
        # RULE: use lowest allowed version for nopytz
        matrix.append(
            {"tox_env": "nopytz", "python_version": f"3.{PYTHON_MINOR_VERSION_MIN}"}
        )
        # RULE: always test the latest version
        matrix.append(
            {"tox_env": "py", "python_version": f"3.{PYTHON_MINOR_VERSION_MAX}"}
        )

    #
    # create full job list if required
    #

    if run_all_jobs:
        for minor_python_version in range(
            PYTHON_MINOR_VERSION_MIN + 1, PYTHON_MINOR_VERSION_MAX
        ):
            matrix.append(
                {"tox_env": "py", "python_version": f"3.{minor_python_version}"}
            )

        # pypy is slow but good to test
        matrix.append({"tox_env": "pypy3", "python_version": "pypy3.10"})

    #
    # Generate tests names for the matrix
    #

    for run in matrix:
        run["test_name"] = run["python_version"]
        if run["tox_env"] != "py":
            run["test_name"] += f" ({run['tox_env']})"

    return matrix


if __name__ == "__main__":
    #
    # always debug to stderr
    #
    stdout = sys.stdout
    sys.stdout = sys.stderr

    #
    # Parse parameters
    #
    arg_ref = sys.argv[1]  # github.ref
    arg_review = sys.argv[2]  # github.event.review.state

    matrix = generate_matrix(arg_ref, arg_review)

    print(json.dumps(matrix, indent=2))  # noqa: T201
    stdout.write(json.dumps(matrix))
