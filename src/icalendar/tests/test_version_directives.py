"""Check that Sphinx version directives use released versions.

``0.0.0`` is allowed until a release replaces it with the release version.
See https://github.com/collective/icalendar/issues/2026
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).parents[3]
VERSION_DIRECTIVE = re.compile(
    r"^\s*\.\.\s+"
    r"(?:version-?added|version-?changed|version-?removed|version-?deprecated|deprecated)"
    r"::\s*(\S+)"
)
RELEASE_BRANCH = re.compile(r"^(?:main|\d+\.x)$")
SOURCE_GLOBS = ("docs/**/*.rst", "src/icalendar/**/*.py")


def _is_release_branch():
    """Return whether the current branch is main or a version branch."""
    branch = os.environ.get("GITHUB_REF_NAME")
    if branch is None:
        try:
            branch = subprocess.run(
                ["git", "branch", "--show-current"],  # noqa: S607
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return False
    return RELEASE_BRANCH.match(branch) is not None


def _released_versions():
    """Return versions that have a Git tag."""
    try:
        result = subprocess.run(
            ["git", "tag", "--list"],  # noqa: S607
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        pytest.skip(f"Git tags are not available: {error}")
    versions = {tag.removeprefix("v") for tag in result.stdout.split()}
    if not versions:
        pytest.skip("No Git tags found. Fetch tags to run this check.")
    return versions


def _version_directives():
    """Yield the location and version of every Sphinx version directive."""
    for pattern in SOURCE_GLOBS:
        for path in sorted(REPOSITORY_ROOT.glob(pattern)):
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                match = VERSION_DIRECTIVE.match(line)
                if match:
                    yield (
                        f"{path.relative_to(REPOSITORY_ROOT)}:{number}",
                        match.group(1),
                    )


def test_version_directives_use_released_versions():
    """Version directives must use a released version or the 0.0.0 placeholder."""
    if _is_release_branch():
        pytest.skip(
            "Version directives are rewritten for a release; checked on pull requests."
        )
    allowed = _released_versions() | {"0.0.0"}
    directives = list(_version_directives())
    assert directives, "No version directives found. The scanner may be broken."
    invalid = {
        location: version for location, version in directives if version not in allowed
    }
    assert not invalid, (
        "Version directives must use a released version or 0.0.0:\n"
        + "\n".join(
            f"  {location}: {version}" for location, version in sorted(invalid.items())
        )
    )
