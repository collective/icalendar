import pytest

from icalendar.error import ICalParsingError
from icalendar.prop import vFrequency, vMonth, vRecur, vWeekday


@pytest.mark.parametrize(
    ("value_type", "value"),
    [
        (vFrequency, "INVALID"),
        (vWeekday, "INVALID"),
        (vMonth, "INVALID"),
    ],
)
def test_value_from_ical_raises_ical_parsing_error(value_type, value):
    with pytest.raises(ICalParsingError) as exc_info:
        value_type.from_ical(value)

    assert exc_info.value.value == value


@pytest.mark.parametrize(
    ("value_type", "value"),
    [
        (vFrequency, "INVALID"),
        (vWeekday, "INVALID"),
        (vMonth, "INVALID"),
    ],
)
def test_value_direct_instantiation_still_raises_value_error(value_type, value):
    with pytest.raises(ValueError) as exc_info:
        value_type(value)

    assert not isinstance(exc_info.value, ICalParsingError)


def test_recur_from_ical_raises_ical_parsing_error():
    value = "FREQ=INVALID"

    with pytest.raises(ICalParsingError) as exc_info:
        vRecur.from_ical(value)

    assert exc_info.value.value == "INVALID"
