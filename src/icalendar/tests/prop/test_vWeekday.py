import pytest

from icalendar.prop import vWeekday


def test_simple():
    weekday = vWeekday("SU")
    assert weekday.to_ical() == b"SU"
    assert weekday.weekday == "SU"
    assert weekday.relative is None


def test_relative():
    weekday = vWeekday("-1MO")
    assert weekday.to_ical() == b"-1MO"
    assert weekday.weekday == "MO"
    assert weekday.relative == -1


def test_roundtrip():
    assert vWeekday.from_ical(vWeekday("+2TH").to_ical()) == "+2TH"


def test_error():
    """Error: Expected weekday abbrevation, got: -100MO"""
    with pytest.raises(ValueError):
        vWeekday.from_ical("-100MO")


@pytest.mark.parametrize("value", ["2MO\n", "MO\n", "+2TH\n", "-1SU\n"])
def test_trailing_newline_rejected(value):
    r"""A trailing line break must not be accepted and carried into the value.

    ``$`` matches just before a final ``\n``, so the newline survived in the
    ``str`` value and was re-emitted into RECUR output (content-line injection).
    """
    with pytest.raises(ValueError):
        vWeekday(value)
    with pytest.raises(ValueError):
        vWeekday.from_ical(value)


def test_ical_value():
    """ical_value property returns the weekday string value."""
    assert vWeekday("MO").ical_value == "MO"
    assert vWeekday("+2TH").ical_value == "+2TH"
    assert vWeekday("-1SU").ical_value == "-1SU"
    assert isinstance(vWeekday("MO").ical_value, str)
