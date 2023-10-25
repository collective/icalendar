"""This file tests the source code provided by the documentation.

See 
- doctest documentation: https://docs.python.org/3/library/doctest.html
- Issue 443: https://github.com/collective/icalendar/issues/443

This file should be tests, too:

    >>> print("Hello World!")
    Hello World!

"""
import doctest
import os
import pytest
import importlib

HERE = os.path.dirname(__file__) or "."
ICALENDAR_PATH = os.path.dirname(HERE)

PYTHON_FILES = [
    os.path.join(dirpath, filename)
    for dirpath, dirnames, filenames in os.walk(ICALENDAR_PATH)
    for filename in filenames if filename.lower().endswith(".py") and 'fuzzing' not in dirpath
]

MODULE_NAMES = [
    "icalendar" + python_file[len(ICALENDAR_PATH):-3].replace("/", ".")
    for python_file in PYTHON_FILES
]

def test_this_module_is_among_them():
    assert __name__ in MODULE_NAMES

@pytest.mark.parametrize("module_name", MODULE_NAMES)
def test_docstring_of_python_file(module_name):
    """This test runs doctest on the Python module."""
    module = importlib.import_module(module_name)
    test_result = doctest.testmod(module, name=module_name)
    assert test_result.failed == 0, f"{test_result.failed} errors in {module_name}"


# This collection needs to exclude .tox and other subdirectories
DOCUMENTATION_PATH = os.path.join(HERE, "../../../")

DOCUMENT_PATHS = [
    os.path.join(DOCUMENTATION_PATH, subdir, filename)
    for subdir in ["docs", "."]
    for filename in os.listdir(os.path.join(DOCUMENTATION_PATH, subdir))
    if filename.lower().endswith(".rst")
]

@pytest.mark.parametrize("filename", [
    "README.rst",
    "index.rst",
])
def test_files_is_included(filename):
    assert any(path.endswith(filename) for path in DOCUMENT_PATHS)

@pytest.mark.parametrize("document", DOCUMENT_PATHS)
def test_documentation_file(document):
    """This test runs doctest on a documentation file."""
    test_result = doctest.testfile(document, module_relative=False)
    assert test_result.failed == 0, f"{test_result.failed} errors in {os.path.basename(document)}"



