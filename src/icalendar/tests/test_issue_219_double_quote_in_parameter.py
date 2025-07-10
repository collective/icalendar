"""This tests handling of the double quote in the parameters.

See https://github.com/collective/icalendar/issues/219
"""

from typing import TYPE_CHECKING

import pytest

from icalendar.parser import unescape_backslashes

if TYPE_CHECKING:
    from icalendar import Alarm, Todo, vText


def test_parse_with_double_quotes(calendars):
    """When we parse the calendar with escaped double quotes, we still need to not error."""
    cal = calendars.issue_219_double_quote_in_parameter
    assert not cal.errors
    todo: Todo = cal.todos[0]
    alarm: Alarm = todo.subcomponents[0]
    assert alarm.uid == "E13840A6-C30C-4BF0-A3E1-73EF27E34BD9"
    apple_location: vText = alarm["X-APPLE-STRUCTURED-LOCATION"]
    p = apple_location.params
    assert p["VALUE"] == "URI"
    print(repr(p["X-ADDRESS"]))
    assert (
        p["X-ADDRESS"]
        == 'Ayacucho 983\nPlata Baja "A"\nC1111AAC CABA\nArgentina\nArgentina'
    )
    assert p["X-APPLE-ABUID"] == "ab://Home"
    assert p["X-APPLE-RADIUS"] == "0"
    assert p["X-APPLE-REFERENCEFRAME"] == "1"
    assert p["X-TITLE"] == "Home"
    assert apple_location == "geo:-34.597613,-58.395858"


@pytest.mark.parametrize(
    ("s", "e"), [("asd", "asd"), ("\\n", "\n"), ("\\\\", "\\"), ("asd\n", "asd\n")]
)
def test_unescape_backslashes(s, e):
    """Check we can escape backslashes properly."""
    assert unescape_backslashes(s) == e, repr(e)
