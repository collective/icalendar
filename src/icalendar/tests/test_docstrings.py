"""Inspect all docstring section headings.
``ALLOWED_HEADINGS`` is a set of allowed headings.
It may be amended as needed.
``KNOWN_BAD_HEADINGS`` is a set of known bad headings.
As docstrings are fixed, their headings may be removed from this set.
See https://github.com/collective/icalendar/issues/1481
"""

import inspect
import re

import pytest

import icalendar

ALLOWED_HEADINGS = {
    "Attributes",
    "Parameters",
    "Returns",
    "Raises",
    "Example",
    "Examples",
    "See also",
    "Attention",
    "Caution",
    "Danger",
    "Hint",
    "Important",
    "Note",
    "Tip",
    "Todo",
}

KNOWN_BAD_HEADINGS = {
    "Availability",
    "Available",
    "BUSYTYPE",
    "CLASS",
    "CUTYPE",
    "Calendar",
    "Conference",
    "Event",
    "FBTYPE",
    "FreeBusy",
    "Image",
    "Journal",
    "PARTSTAT",
    "Parameters",
    "RANGE",
    "RELATED",
    "RELTYPE",
    "ROLE",
    "STATUS",
    "TRANSP",
    "Todo",
    "VALUE",
    "vCalAddress",
    "vDate",
    "vDatetime",
    "vDuration",
    "vFloat",
    "vGeo",
    "vInt",
    "vMonth",
    "vPeriod",
    "vRecur",
    "vTime",
    "vUTCOffset",
    "vUri",
}


def get_public_objects():
    objs = []
    # Test on the main public module for now to establish baseline
    for name, obj in inspect.getmembers(icalendar):
        if name.startswith("_"):
            continue
        if inspect.isclass(obj) or inspect.isfunction(obj):
            objs.append(obj)
    return objs


def _obj_id(obj):
    """Return the name of the object for parametrize IDs."""
    return obj.__name__


@pytest.mark.parametrize("obj", get_public_objects(), ids=_obj_id)
def test_docstring_headings_are_valid(obj):
    """
    Identify docstring section headings that are not one of the allowed types.
    """
    if obj.__name__ in KNOWN_BAD_HEADINGS:
        pytest.xfail(
            f"'{obj.__module__}.{obj.__qualname__}'\n"
            "  Invalid docstring section heading. See:\n"
            "  https://icalendar.readthedocs.io/en/stable/contribute/documentation/style-guide.html#docstring-structure"
        )

    doc = inspect.getdoc(obj)
    if not doc:
        return

    # Match standard docstring headings (Word(s) followed by a colon)
    headings = re.findall(
        r"^ *([A-Z][A-Za-z]+(?: [A-Za-z]+)*):(?:\n|$)", doc, re.MULTILINE
    )

    for heading in headings:
        assert heading in ALLOWED_HEADINGS, (
            f"Invalid docstring heading '{heading}' found in '{obj.__name__}'. "
            f"Allowed headings are: {', '.join(sorted(ALLOWED_HEADINGS))}"
        )


def get_all_public_methods_and_functions():
    objs = []
    # Test on the main public module for now to establish baseline
    for obj in get_public_objects():
        if inspect.isfunction(obj):
            objs.append(obj)
        elif inspect.isclass(obj):
            for name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if name.startswith("_") and name != "__init__":
                    continue
                objs.append(method)
    return objs


def _method_id(obj):
    return obj.__qualname__


@pytest.mark.parametrize("obj", get_all_public_methods_and_functions(), ids=_method_id)
def test_docstring_has_parameters_section(obj):
    """
    Identify docstrings that lack a Parameters section when the Python object's signature accepts parameters other than self.
    """
    try:
        sig = inspect.signature(obj)
    except ValueError:
        return

    params = [p for n, p in sig.parameters.items() if n not in ("self", "cls")]
    if not params:
        return

    doc = inspect.getdoc(obj)
    if not doc:
        return

    if not re.search(r"^Parameters:$", doc, re.MULTILINE):
        pytest.xfail(
            f"'{obj.__module__}.{obj.__qualname__}' lacks a Parameters section."
        )


def check_returns_and_raises(obj):
    try:
        source = inspect.getsource(obj)
        source = inspect.cleandoc(source)
        import ast

        tree = ast.parse(source)
    except (OSError, TypeError, SyntaxError):
        return False, False

    has_returns = False
    has_raises = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Return) and node.value is not None:
            has_returns = True
        if isinstance(node, ast.Raise):
            has_raises = True

    return has_returns, has_raises


@pytest.mark.parametrize("obj", get_all_public_methods_and_functions(), ids=_method_id)
def test_docstring_has_returns_section(obj):
    """
    Identify docstrings for Python objects that return something, but lack a Returns section heading.
    """
    has_ret, _ = check_returns_and_raises(obj)
    if not has_ret:
        return

    doc = inspect.getdoc(obj)
    if not doc:
        return

    if not re.search(r"^Returns:$", doc, re.MULTILINE):
        pytest.xfail(
            f"'{obj.__module__}.{obj.__qualname__}' returns a value but lacks a Returns section."
        )


@pytest.mark.parametrize("obj", get_all_public_methods_and_functions(), ids=_method_id)
def test_docstring_has_raises_section(obj):
    """
    Identify docstrings for Python objects that raise something, but lack a Raises section heading.
    """
    _, has_raise = check_returns_and_raises(obj)
    if not has_raise:
        return

    doc = inspect.getdoc(obj)
    if not doc:
        return

    if not re.search(r"^Raises:$", doc, re.MULTILINE):
        pytest.xfail(
            f"'{obj.__module__}.{obj.__qualname__}' raises an exception but lacks a Raises section."
        )


@pytest.mark.parametrize("obj", get_all_public_methods_and_functions(), ids=_method_id)
def test_docstring_has_examples_section(obj):
    """
    Identify docstrings with both a summary and description, but lack an Example.
    """
    doc = inspect.getdoc(obj)
    if not doc:
        return

    lines = doc.strip().split("\n")
    if len(lines) < 3 or lines[1].strip() != "":
        # Doesn't have a clear summary and description separated by a blank line
        return

    if not re.search(r"^(Example|Examples):$", doc, re.MULTILINE):
        pytest.xfail(
            f"'{obj.__module__}.{obj.__qualname__}' has a summary and description but lacks an Example section."
        )
