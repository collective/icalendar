"""Ensure no __init__ or __new__ method carries a docstring.

Sphinx appends __init__/__new__ docstrings to the class docstring,
producing confusing output.  All constructor documentation must live
in the class docstring itself.

See https://github.com/collective/icalendar/issues/1620
"""

import ast
import pathlib

import pytest

SRC = pathlib.Path(__file__).resolve().parents[1]


def _iter_init_docstrings():
    """Yield (file, class, method, lineno) for every __init__/__new__
    that has a docstring."""
    for py in SRC.rglob("*.py"):
        if "tests" in py.parts or "__pycache__" in py.parts:
            continue
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for item in node.body:
                if (
                    isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name in ("__init__", "__new__")
                    and ast.get_docstring(item) is not None
                ):
                    yield (
                        str(py.relative_to(SRC)),
                        node.name,
                        item.name,
                        item.lineno,
                    )


def test_no_init_or_new_docstrings():
    offenders = list(_iter_init_docstrings())
    if offenders:
        lines = [
            f"  {f}:{ln} {cls}.{meth}"
            for f, cls, meth, ln in offenders
        ]
        pytest.fail(
            "Found __init__/__new__ methods with docstrings "
            "(move them to the class docstring):\n" + "\n".join(lines)
        )
