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
