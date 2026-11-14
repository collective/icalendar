"""Test the ical_value property of vInline."""

import pytest

from icalendar import Event
from icalendar.prop import vInline


@pytest.mark.parametrize(
    "text",
    [
        "Some text",
        "",
        'Chair,Table,"Room: 42"',
        "Grüße, 世界",
    ],
)
def test_ical_value(text):
    """ical_value returns the unparsed text as a plain str."""
    value = vInline(text).ical_value
    assert value == text
    assert type(value) is str


def test_ical_value_from_bytes():
    """ical_value is the decoded text when the value is created from bytes."""
    assert vInline("Grüße".encode()).ical_value == "Grüße"


def test_ical_value_from_ical():
    """ical_value also works when the value is created with from_ical."""
    value = vInline.from_ical("Chair,Table").ical_value
    assert value == "Chair,Table"
    assert type(value) is str


def test_decoded_uses_ical_value():
    """Component.decoded() returns the ical_value of an inline value."""
    event = Event()
    event.set_inline("RESOURCES", ["Chair", "Table"])
    assert event.decoded("RESOURCES") == "Chair,Table"
