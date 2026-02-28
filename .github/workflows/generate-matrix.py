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


#
# always debug to stderr
#
stdout = sys.stdout
sys.stdout = sys.stderr

#
# Parse parameters
#
ARG_REF = sys.argv[1]  # github.ref
ARG_PR = sys.argv[2]  # github.event.review.state

#
# Create run conditions
#
RUNS_ON_MAIN = ARG_REF == "refs/heads/main"
RUNS_ON_STABLE = bool(re.match(r"refs/heads/\d+\.x", ARG_REF))
RUNS_ON_TAGS = ARG_REF.startswith("refs/tags/v")
PR_IS_APPROVED = ARG_PR == "approved"

RUN_ALL_JOBS = RUNS_ON_MAIN or RUNS_ON_TAGS or PR_IS_APPROVED or RUNS_ON_STABLE

#
# Debug conditions
#
for k, v in sorted(locals().items()):
    if isinstance(v, (bool, str, int)) and not k.startswith("_"):
        print(f"{k} = {v!r}")  # noqa: T201

#
# Create matrix
#
matrix = []

#
# jobs that always run
#
# RULE: always test the lowest allowed version
matrix.append({"tox_env": "py", "python_version": f"3.{PYTHON_MINOR_VERSION_MIN}"})
# RULE: use lowest allowed version for nopytz
matrix.append({"tox_env": "nopytz", "python_version": f"3.{PYTHON_MINOR_VERSION_MIN}"})
# RULE: always test the latest version
matrix.append({"tox_env": "py", "python_version": f"3.{PYTHON_MINOR_VERSION_MAX}"})

#
# create full job list if required
#

if RUN_ALL_JOBS:
    for minor_python_version in range(
        PYTHON_MINOR_VERSION_MIN + 1, PYTHON_MINOR_VERSION_MAX
    ):
        matrix.append({"tox_env": "py", "python_version": f"3.{minor_python_version}"})

    # pypy is slow but good to test
    matrix.append({"tox_env": "pypy3", "python_version": "pypy3.10"})

#
# Generate tests names for the matrix
#

for run in matrix:
    run["test_name"] = run["python_version"]
    if run["tox_env"] != "py":
        run["test_name"] += f" ({run['tox_env']})"

print(json.dumps(matrix, indent=2))  # noqa: T201
stdout.write(json.dumps(matrix))
