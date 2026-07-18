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


def get_public_objects():
    objs = []
    # Test on the main public module for now to establish baseline
    for name, obj in inspect.getmembers(icalendar):
        if name.startswith("_"):
            continue
        if inspect.isclass(obj) or inspect.isfunction(obj):
            objs.append(obj)
    return objs


@pytest.mark.parametrize("obj", get_public_objects())
def test_docstring_headings_are_valid(obj):
    """
    Identify section headings that are not one of the allowed types.
    """
    doc = inspect.getdoc(obj)
    if not doc:
        return

    # Match standard docstring headings (Word(s) followed by a colon)
    headings = re.findall(r"^[ \t]*([A-Z][A-Za-z]+(?: [A-Za-z]+)*):[ \t]*$", doc, re.MULTILINE)

    for heading in headings:
        assert heading in ALLOWED_HEADINGS, (
            f"Invalid docstring heading '{heading}' found in '{obj.__name__}'. "
            f"Allowed headings are: {', '.join(sorted(ALLOWED_HEADINGS))}"
        )
