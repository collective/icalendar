"""Tests for the structure and quality of icalendar's docstrings.

These tests walk the public classes, functions, and methods of the
``icalendar`` package and check their docstrings against the conventions
described in the documentation style guide:
https://icalendar.readthedocs.io/en/latest/contribute/documentation/style-guide.html#docstring-structure

A docstring's summary, its optional description, and its examples are
already exercised as doctests by ``test_with_doctest.py``.
This module checks *structure* instead: whether the section headings used
are ones icalendar recognizes, and whether a Parameters, Returns, Raises,
or Examples section is present when the signature or body of the object
suggests one is needed.

Many existing docstrings in icalendar predate these conventions and don't
yet comply.
Rather than fail the whole suite for every pre-existing issue at once,
known violations are recorded in ``docstring_known_violations.json``,
next to this file.
That file acts as a ratchet:

-   An object listed there is allowed to keep failing for now, tracked
    under :issue:`1481` and its related docstring-cleanup issues
    (:issue:`1244`, :issue:`1182`, :issue:`1072`, :issue:`1007`,
    :issue:`938`).
-   If a listed object's docstring is fixed, its check switches from
    "expected failure" to an unexpected pass, which this suite reports as
    a hard failure until its entry is removed from the JSON file.
-   Any object *not* listed is expected to comply now, so new code and
    newly written docstrings are held to the full standard immediately.

To refresh the baseline after intentionally fixing or introducing
docstrings, run:

.. code-block:: shell

    python src/icalendar/tests/generate_docstring_baseline.py
"""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import pkgutil
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

import icalendar

if TYPE_CHECKING:
    from collections.abc import Callable

HERE = Path(__file__).resolve().parent
BASELINE_PATH = HERE / "docstring_known_violations.json"

# Modules that aren't part of the public, documented API surface.
SKIP_MODULE_PREFIXES = ("icalendar.tests", "icalendar.hypothesis")

# Section headings recognized by icalendar's docstring style guide.
ALLOWED_SECTIONS = frozenset(
    {
        "attributes",
        "parameters",
        "returns",
        "raises",
        "example",
        "examples",
    }
)

# Standard Sphinx/Napoleon admonitions, allowed anywhere as headings.
ALLOWED_ADMONITIONS = frozenset(
    {
        "attention",
        "caution",
        "danger",
        "error",
        "hint",
        "important",
        "note",
        "see also",
        "tip",
        "todo",
        "warning",
    }
)

ALLOWED_HEADINGS = ALLOWED_SECTIONS | ALLOWED_ADMONITIONS

# A line of a dedented docstring is a section heading when it sits at the
# base indentation, is one to three title-like words, and ends in a colon
# with nothing else on the line.
_HEADING_RE = re.compile(r"^([A-Z][A-Za-z]*(?: [A-Za-z]+){0,2}):\s*$")


@dataclass(frozen=True)
class DocumentedObject:
    """A single class, function, or method collected for docstring checks."""

    qualname: str
    obj: Callable[..., Any] | type
    kind: str  # "class", "function", or "method"
    is_init: bool = False


def _is_public(name: str) -> bool:
    return name == "__init__" or not name.startswith("_")


def _unwrap(value: Any) -> Any:
    if isinstance(value, (staticmethod, classmethod)):
        return value.__func__
    if isinstance(value, property):
        return value.fget
    return value


def iter_package_modules():
    """Yield every importable, non-test module of the icalendar package."""
    for info in pkgutil.walk_packages(icalendar.__path__, prefix="icalendar."):
        if any(
            info.name == prefix or info.name.startswith(prefix + ".")
            for prefix in SKIP_MODULE_PREFIXES
        ):
            continue
        try:
            yield importlib.import_module(info.name)
        except ImportError:
            continue


def collect_documented_objects() -> list[DocumentedObject]:
    """Collect every public class, function, and method to check."""
    objects: list[DocumentedObject] = []
    seen: set[int] = set()

    for module in iter_package_modules():
        for name, member in vars(module).items():
            if (
                not _is_public(name)
                or getattr(member, "__module__", None) != module.__name__
            ):
                continue

            if inspect.isclass(member):
                if id(member) in seen:
                    continue
                seen.add(id(member))
                objects.append(
                    DocumentedObject(f"{module.__name__}.{name}", member, "class")
                )
                for attr_name, attr_value in vars(member).items():
                    if not _is_public(attr_name):
                        continue
                    func = _unwrap(attr_value)
                    if not inspect.isfunction(func) or id(func) in seen:
                        continue
                    seen.add(id(func))
                    objects.append(
                        DocumentedObject(
                            f"{module.__name__}.{name}.{attr_name}",
                            func,
                            "method",
                            is_init=attr_name == "__init__",
                        )
                    )
            elif inspect.isfunction(member):
                if id(member) in seen:
                    continue
                seen.add(id(member))
                objects.append(
                    DocumentedObject(f"{module.__name__}.{name}", member, "function")
                )

    return objects


DOCUMENTED_OBJECTS = sorted(
    collect_documented_objects(), key=lambda item: item.qualname
)


def _headings_of(docstring: str) -> list[str]:
    """Return the section headings found in a dedented docstring."""
    lines = docstring.splitlines()
    headings = []
    for index, line in enumerate(lines):
        if index == 0:
            # The summary line is never a heading, even if it ends in ':'.
            continue
        match = _HEADING_RE.match(line)
        if match is None:
            continue
        previous = lines[index - 1].strip()
        if previous:
            # Headings are preceded by a blank line (or are the first line
            # after the summary/description block ends).
            continue
        headings.append(match.group(1))
    return headings


def _has_description(docstring: str) -> bool:
    """Whether a docstring has a description paragraph beyond its summary."""
    lines = docstring.splitlines()
    body = "\n".join(lines[1:]).strip()
    if not body:
        return False
    first_heading = next(
        (
            index
            for index, line in enumerate(lines[1:], start=1)
            if _HEADING_RE.match(line) and not lines[index - 1].strip()
        ),
        len(lines),
    )
    description = "\n".join(lines[1:first_heading]).strip()
    return bool(description)


def _signature_parameters(obj: Callable[..., Any]) -> list[str]:
    try:
        signature = inspect.signature(obj)
    except (TypeError, ValueError):
        return []
    return [
        param.name
        for param in signature.parameters.values()
        if param.name not in ("self", "cls")
        and param.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]


def _returns_value(func: Callable[..., Any]) -> bool:
    signature = inspect.signature(func)
    if signature.return_annotation not in (inspect.Signature.empty, None, "None"):
        return True
    try:
        source = textwrap.dedent(inspect.getsource(func))
    except (OSError, TypeError):
        return False
    tree = ast.parse(source)
    function_node = tree.body[0]
    for node in ast.walk(function_node):
        # Don't descend into nested functions: their returns aren't ours.
        if node is not function_node and isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        ):
            continue
        if isinstance(node, ast.Return) and node.value is not None:
            return True
    return False


def _raises_exception(func: Callable[..., Any]) -> bool:
    try:
        source = textwrap.dedent(inspect.getsource(func))
    except (OSError, TypeError):
        return False
    tree = ast.parse(source)
    function_node = tree.body[0]
    for node in ast.walk(function_node):
        if node is not function_node and isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        ):
            continue
        if isinstance(node, ast.Raise) and node.exc is not None:
            return True
    return False


@dataclass(frozen=True)
class CheckResult:
    """The outcome of running one docstring check against one object."""

    applicable: bool
    ok: bool = True
    message: str = ""


def check_headings(documented: DocumentedObject) -> CheckResult:
    """A docstring's section headings must all be ones icalendar recognizes."""
    docstring = inspect.getdoc(documented.obj)
    if not docstring:
        return CheckResult(applicable=False)

    allowed = ALLOWED_HEADINGS
    if documented.kind == "class":
        # A class docstring must not describe its constructor: that
        # belongs on __init__, which Sphinx appends automatically.
        allowed = ALLOWED_ADMONITIONS | {"attributes", "example", "examples"}

    invalid = [h for h in _headings_of(docstring) if h.lower() not in allowed]
    if invalid:
        return CheckResult(
            applicable=True,
            ok=False,
            message=(
                f"{documented.qualname} has unrecognized docstring heading(s): "
                f"{', '.join(invalid)}. Allowed headings: {sorted(allowed)}."
            ),
        )
    return CheckResult(applicable=True)


def check_parameters(documented: DocumentedObject) -> CheckResult:
    """A Parameters section is required when there are parameters to document."""
    if documented.kind == "class":
        return CheckResult(applicable=False)
    docstring = inspect.getdoc(documented.obj)
    if not docstring or not _signature_parameters(documented.obj):
        return CheckResult(applicable=False)

    headings = {h.lower() for h in _headings_of(docstring)}
    if "parameters" not in headings:
        return CheckResult(
            applicable=True,
            ok=False,
            message=(
                f"{documented.qualname} takes parameters but its docstring "
                "has no Parameters section."
            ),
        )
    return CheckResult(applicable=True)


def check_returns(documented: DocumentedObject) -> CheckResult:
    """A Returns section is required when the function returns a value."""
    if documented.kind == "class" or documented.is_init:
        return CheckResult(applicable=False)
    docstring = inspect.getdoc(documented.obj)
    if not docstring or not _returns_value(documented.obj):
        return CheckResult(applicable=False)

    headings = {h.lower() for h in _headings_of(docstring)}
    if "returns" not in headings:
        return CheckResult(
            applicable=True,
            ok=False,
            message=(
                f"{documented.qualname} returns a value but its docstring "
                "has no Returns section."
            ),
        )
    return CheckResult(applicable=True)


def check_raises(documented: DocumentedObject) -> CheckResult:
    """A Raises section is required when the function raises an exception."""
    if documented.kind == "class":
        return CheckResult(applicable=False)
    docstring = inspect.getdoc(documented.obj)
    if not docstring or not _raises_exception(documented.obj):
        return CheckResult(applicable=False)

    headings = {h.lower() for h in _headings_of(docstring)}
    if "raises" not in headings:
        return CheckResult(
            applicable=True,
            ok=False,
            message=(
                f"{documented.qualname} raises an exception but its "
                "docstring has no Raises section."
            ),
        )
    return CheckResult(applicable=True)


def check_examples(documented: DocumentedObject) -> CheckResult:
    """A described docstring should show usage in an Examples section."""
    docstring = inspect.getdoc(documented.obj)
    if not docstring or not _has_description(docstring):
        return CheckResult(applicable=False)

    headings = {h.lower() for h in _headings_of(docstring)}
    if not headings & {"example", "examples"}:
        return CheckResult(
            applicable=True,
            ok=False,
            message=(
                f"{documented.qualname} has a description but its "
                "docstring has no Examples section."
            ),
        )
    return CheckResult(applicable=True)


CHECKS: dict[str, Callable[[DocumentedObject], CheckResult]] = {
    "headings": check_headings,
    "parameters": check_parameters,
    "returns": check_returns,
    "raises": check_raises,
    "examples": check_examples,
}


def load_baseline() -> dict[str, set[str]]:
    if not BASELINE_PATH.exists():
        return {name: set() for name in CHECKS}
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    return {name: set(data.get(name, [])) for name in CHECKS}


BASELINE = load_baseline()


def _params_for(check_name: str):
    """Build parametrize params, marking known violations as expected."""
    known = BASELINE[check_name]
    params = []
    for documented in DOCUMENTED_OBJECTS:
        marks = []
        if documented.qualname in known:
            marks.append(
                pytest.mark.xfail(
                    reason=(
                        "known pre-existing docstring violation, tracked "
                        "under issue #1481; run "
                        "generate_docstring_baseline.py to refresh after "
                        "a fix"
                    ),
                    strict=True,
                )
            )
        params.append(pytest.param(documented, id=documented.qualname, marks=marks))
    return params


@pytest.mark.parametrize("documented", _params_for("headings"))
def test_docstring_headings_are_recognized(documented: DocumentedObject) -> None:
    """Every docstring section heading must be one icalendar recognizes."""
    result = check_headings(documented)
    if not result.applicable:
        pytest.skip("no docstring to check")
    assert result.ok, result.message


@pytest.mark.parametrize("documented", _params_for("parameters"))
def test_docstring_has_parameters_section(documented: DocumentedObject) -> None:
    """A Parameters section is required when there are parameters to document."""
    result = check_parameters(documented)
    if not result.applicable:
        pytest.skip("no parameters to document, or no docstring")
    assert result.ok, result.message


@pytest.mark.parametrize("documented", _params_for("returns"))
def test_docstring_has_returns_section(documented: DocumentedObject) -> None:
    """A Returns section is required when the function returns a value."""
    result = check_returns(documented)
    if not result.applicable:
        pytest.skip("does not return a value, or no docstring")
    assert result.ok, result.message


@pytest.mark.parametrize("documented", _params_for("raises"))
def test_docstring_has_raises_section(documented: DocumentedObject) -> None:
    """A Raises section is required when the function raises an exception."""
    result = check_raises(documented)
    if not result.applicable:
        pytest.skip("does not raise an exception, or no docstring")
    assert result.ok, result.message


@pytest.mark.parametrize("documented", _params_for("examples"))
def test_docstring_with_description_has_examples(documented: DocumentedObject) -> None:
    """A described docstring should show usage in an Examples section."""
    result = check_examples(documented)
    if not result.applicable:
        pytest.skip("no description beyond the summary, or no docstring")
    assert result.ok, result.message


def test_documented_objects_were_collected() -> None:
    """Sanity check that the collection walk actually found objects."""
    assert len(DOCUMENTED_OBJECTS) > 100


def test_baseline_has_no_stale_qualnames() -> None:
    """Every qualname in the baseline must refer to an object we still see."""
    known_qualnames = {item.qualname for item in DOCUMENTED_OBJECTS}
    for check_name, qualnames in BASELINE.items():
        stale = qualnames - known_qualnames
        assert not stale, (
            f"docstring_known_violations.json lists stale {check_name} "
            f"entries no longer found in the codebase: {sorted(stale)}. "
            "Regenerate it with generate_docstring_baseline.py."
        )
