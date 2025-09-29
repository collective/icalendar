"""This tests the documentation of icalendar.

See `PR 822 <https://github.com/collective/icalendar/pull/822#discussion_r2385523339>`__.
"""

from __future__ import annotations

from pathlib import Path

import pytest

## Configuration ##

# Modules that are not considered for documentation
# because they are private or otherwise not relevant.
EXCLUDED_MODULES = {
    "icalendar.tests.conftest",  # only for tests
    "icalendar.tests.timezone_ids",  # only for tests
    "icalendar.fuzzing.ical_fuzzer",  # only for fuzzing
    "icalendar.cal.examples",  # only for examples, exposed through components
}

# Reference files that are not considered to match a module.
EXCLUDED_REFERENCE_FILES = {
    "modules",  # TODO: why is this here?
}

## Tests ##

HERE = Path(__file__).parent
DOCS = HERE.parent.parent.parent / "docs"

if not DOCS.exists():
    # we might need to skip this if we have a package installation
    # without docs
    pytest.skip("No docs found", allow_module_level=True)


DOCS_REFERENCE_FILES = {file.stem for file in (DOCS / "reference").glob("*.rst")}

DOCUMENTED_MODULES = DOCS_REFERENCE_FILES - EXCLUDED_REFERENCE_FILES

ICALENDAR_BASE_PATH = HERE.parent.parent.absolute()


def convert_python_file_to_module(file: Path) -> str:
    """Convert a python file path to a module name."""
    relative = file.absolute().relative_to(ICALENDAR_BASE_PATH)
    parts = relative.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


PYTHON_MODULES = {
    convert_python_file_to_module(file)
    for file in (HERE.parent).glob("**/*.py")
    # exclude test files
    if not file.name.startswith("test_")
    # exclude private modules
    and not (file.stem.startswith("_") and file.stem != "__init__")
} - EXCLUDED_MODULES


def test_all_python_modules_are_documented():
    """Test that all python modules are documented."""
    undocumented = PYTHON_MODULES - DOCUMENTED_MODULES
    message = f"""{", ".join(undocumented)} are undocumented.

    Please add documentation for them in docs/reference.

    If they only contain private code, you can ignore them
    by editing the name to EXCLUDED_MODULES in this test file.
    """
    assert not undocumented, message


def test_reference_documentation_refers_to_an_existing_module():
    """Test that all documented modules exist."""
    nonexisting = DOCUMENTED_MODULES - PYTHON_MODULES
    message = f"""{", ".join(nonexisting)} don't have a corresponding module.

    Please remove them from the documentation in docs/reference or
    rename them to match an existing module.

    If they are correct, you can ignore them by adding the name to
    EXCLUDED_REFERENCE_FILES in this test file.
    """
    assert not nonexisting, message
