from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

SOURCE_ROOT = Path(__file__).parents[1]
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
    "Tip",
    "Todo",
    "Value Name",
    "Value Type",
    "Values",
}


def _iter_source_files() -> list[Path]:
    return [
        path
        for path in sorted(SOURCE_ROOT.rglob("*.py"))
        if "tests" not in path.parts and "fuzzing" not in path.parts
    ]


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
    for path in _iter_source_files():
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
