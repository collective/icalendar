import pytest

from icalendar.error import InvalidCalendar
from icalendar.prop import vFrequency, vRecur


@pytest.mark.parametrize(
    "frequency",
    ["SECONDLY", "MINUTELY", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "YEARLY"],
)
def test_freq_returns_the_registered_frequency_type(frequency):
    recur = vRecur.from_ical(f"FREQ={frequency}")

    assert isinstance(recur.freq, vRecur.types["FREQ"])
    assert isinstance(recur.freq, vFrequency)
    assert recur.freq == frequency


def test_freq_is_required():
    with pytest.raises(InvalidCalendar, match="FREQ is required"):
        vRecur().freq


def test_freq_empty_value_is_invalid():
    with pytest.raises(InvalidCalendar, match="FREQ is required"):
        vRecur(FREQ=[]).freq


def test_freq_returns_the_first_value_when_multiple_are_stored():
    recur = vRecur(FREQ=["WEEKLY", "DAILY"])

    assert recur.freq == "WEEKLY"


@pytest.mark.parametrize("value", ["BOGUS", "", 42])
def test_freq_rejects_invalid_stored_values(value):
    recur = vRecur(FREQ=[value])

    with pytest.raises(InvalidCalendar, match="FREQ must be a valid frequency"):
        recur.freq


def test_setting_freq_stores_a_normalized_frequency():
    recur = vRecur()

    recur.freq = "weekly"

    assert recur.freq == "WEEKLY"
    assert isinstance(recur["FREQ"][0], vFrequency)
    assert recur.to_ical() == b"FREQ=WEEKLY"


def test_setting_freq_rejects_invalid_values_without_changing_the_rule():
    recur = vRecur.from_ical("FREQ=DAILY")

    with pytest.raises(InvalidCalendar, match="FREQ must be a valid frequency"):
        recur.freq = "BOGUS"

    assert recur.freq == "DAILY"


def test_freq_cannot_be_set_to_none():
    recur = vRecur.from_ical("FREQ=DAILY")

    with pytest.raises(InvalidCalendar, match="FREQ is required"):
        recur.freq = None

    assert recur.freq == "DAILY"


def test_freq_cannot_be_deleted():
    recur = vRecur.from_ical("FREQ=DAILY")

    with pytest.raises(InvalidCalendar, match="FREQ is required"):
        del recur.freq

    assert recur.freq == "DAILY"


def test_setting_freq_accepts_registered_frequency_type():
    recur = vRecur()
    frequency = vFrequency.from_ical("DAILY")

    recur.freq = frequency

    assert isinstance(recur.freq, vRecur.types["FREQ"])
    assert recur.freq == frequency


def test_from_ical_matches_setting_freq():
    parsed = vRecur.from_ical("FREQ=DAILY")
    assigned = vRecur()
    assigned.freq = "DAILY"

    assert parsed == assigned


def test_freq_roundtrips_through_ical():
    recur = vRecur.from_ical("FREQ=WEEKLY;COUNT=3")
    roundtripped = vRecur.from_ical(recur.to_ical().decode())

    assert roundtripped.freq == "WEEKLY"
