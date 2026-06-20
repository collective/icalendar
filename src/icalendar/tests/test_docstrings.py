"""Inspect the structure and section headings of public docstrings."""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

import icalendar
from icalendar.tests.test_with_doctest import PYTHON_FILES

SOURCE_ROOT = Path(__file__).parents[1].resolve()
SECTION_HEADING_RE = re.compile(r"^([A-Za-z][A-Za-z ]+):$")
ALLOWED_SECTION_HEADINGS = {
    "Attributes",
    "Attention",
    "Caution",
    "Conformance",
    "Danger",
    "Definition from RFC",
    "Description",
    "Example",
    "Example with parameter",
    "Example without parameters",
    "Examples",
    "Format Definition",
    "Hint",
    "Important",
    "Note",
    "Parameters",
    "Property Name",
    "Property Parameters",
    "Purpose",
    "Raises",
    "Returns",
    "See Also",
    "See also",
    "Tip",
    "Todo",
    "Value Name",
    "Value Type",
    "Values",
}


def _is_public_name(name: str) -> bool:
    return not name.startswith("_") or name == "__init__"


def _module_name(path: Path) -> str:
    return ".".join(path.relative_to(SOURCE_ROOT.parent).with_suffix("").parts)


def _iter_public_docstrings(node: ast.AST, qualname: str) -> list[tuple[str, str]]:
    if not isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
        return []
    if not _is_public_name(node.name):
        return []

    node_qualname = f"{qualname}.{node.name}"
    docstring = ast.get_docstring(node)
    result = [(node_qualname, docstring)] if docstring else []

    if isinstance(node, ast.ClassDef):
        for child in node.body:
            result.extend(_iter_public_docstrings(child, node_qualname))

    return result


def _collect_public_docstrings() -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for python_file in PYTHON_FILES:
        path = python_file.resolve()
        if "tests" in path.relative_to(SOURCE_ROOT).parts:
            continue
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in module.body:
            result.extend(_iter_public_docstrings(node, _module_name(path)))
    return result


def _unsupported_section_headings(docstring: str) -> list[str]:
    headings: list[str] = []
    for line in docstring.splitlines():
        match = SECTION_HEADING_RE.match(line)
        if match and match.group(1) not in ALLOWED_SECTION_HEADINGS:
            headings.append(match.group(1))
    return sorted(set(headings))


PUBLIC_DOCSTRINGS = _collect_public_docstrings()


@pytest.mark.parametrize(("qualname", "docstring"), PUBLIC_DOCSTRINGS)
def test_public_docstring_section_headings_are_supported(
    qualname: str, docstring: str
) -> None:
    unsupported_headings = _unsupported_section_headings(docstring)

    assert not unsupported_headings, (
        f"{qualname} uses unsupported docstring section heading(s): "
        f"{', '.join(unsupported_headings)}. Use one of: "
        f"{', '.join(sorted(ALLOWED_SECTION_HEADINGS))}."
    )


def test_unsupported_section_headings_reject_args() -> None:
    docstring = """Create a thing.

Args:
    value: The value.
"""

    assert _unsupported_section_headings(docstring) == ["Args"]


def get_public_objects():
    objs = []
    # Test on the main public module for now to establish baseline
    for name, obj in inspect.getmembers(icalendar):
        if name.startswith("_"):
            continue
        if inspect.isclass(obj) or inspect.isfunction(obj):
            objs.append(obj)
    return objs


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
