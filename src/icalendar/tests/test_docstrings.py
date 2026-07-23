"""Inspect all docstring section headings.
``ALLOWED_HEADINGS`` is a set of allowed headings.
It may be amended as needed.
``KNOWN_BAD_HEADINGS`` is a set of known bad headings.
As docstrings are fixed, their headings may be removed from this set.
``KNOWN_MISSING_PARAMETERS`` is a set of functions and methods whose
docstrings lack a ``Parameters`` section.
As docstrings are fixed, their names may be removed from this set.
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

KNOWN_MISSING_PARAMETERS = {
    "Alarms.__init__",
    "Conference.__init__",
    "ICalParsingError.__init__",
    "Image.__init__",
    "is_utc",
    "vBinary.__init__",
    "vCategory.__init__",
    "vDDDLists.__init__",
    "vDDDTypes.__init__",
    "vDate.__init__",
    "vDatetime.__init__",
    "vDuration.__init__",
    "vGeo.__init__",
    "vPeriod.__init__",
    "vTime.__init__",
    "vUTCOffset.__init__",
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


def get_public_objects_with_parameters():
    """Return public functions and ``__init__`` methods with parameters.

    For each public object, select the function itself or, for a class, the
    ``__init__`` method defined by that class. Keep only those whose
    signatures accept parameters other than ``self`` and ``cls``, excluding
    ``*args`` and ``**kwargs``.
    """
    functions = []
    for obj in get_public_objects():
        # A class's docstring must not contain a Parameters section.
        # Sphinx appends the __init__ docstring to the class docstring.
        if inspect.isclass(obj):
            function = obj.__dict__.get("__init__")
            if not inspect.isfunction(function):
                continue
        else:
            function = obj
        try:
            signature = inspect.signature(function)
        except (ValueError, TypeError):
            continue
        parameters = [
            parameter
            for name, parameter in signature.parameters.items()
            if name not in ("self", "cls")
            and parameter.kind not in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD)
        ]
        if parameters:
            functions.append(function)
    return functions


def _obj_id(obj):
    """Return the name of the object for parametrize IDs."""
    return obj.__name__


def _function_id(function):
    """Return the qualified name of the function for parametrize IDs."""
    return function.__qualname__


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


@pytest.mark.parametrize(
    "function", get_public_objects_with_parameters(), ids=_function_id
)
def test_docstring_has_parameters_section(function):
    """
    Identify docstrings that lack a Parameters section when the signature
    accepts parameters other than self.
    """
    if function.__qualname__ in KNOWN_MISSING_PARAMETERS:
        pytest.xfail(
            f"'{function.__module__}.{function.__qualname__}'\n"
            "  Missing 'Parameters' docstring section. See:\n"
            "  https://icalendar.readthedocs.io/en/stable/contribute/documentation/style-guide.html#docstring-structure"
        )

    doc = inspect.getdoc(function) or ""
    assert re.search(r"^\s*Parameters:\s*$", doc, re.MULTILINE), (
        "Missing 'Parameters' docstring section in "
        f"'{function.__module__}.{function.__qualname__}', whose signature "
        "accepts parameters other than 'self'. See: "
        "https://icalendar.readthedocs.io/en/stable/contribute/documentation/style-guide.html#docstring-structure"
    )
