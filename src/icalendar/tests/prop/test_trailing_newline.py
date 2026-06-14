r"""A trailing line break must not be accepted by the value validation regexes.

``$`` matches just before a final ``\n``, so a value with a trailing line break
was accepted by ``DURATION_REGEX``, ``TIME_JCAL_REGEX`` and
``UTC_OFFSET_JCAL_REGEX``. The regexes are now anchored with ``\Z``.
"""

import pytest

from icalendar.error import InvalidCalendar, JCalParsingError
from icalendar.prop import vDuration, vTime, vUTCOffset


@pytest.mark.parametrize("value", ["P1D\n", "P7W\n", "PT1H0M22S\n"])
def test_vDuration_from_ical_rejects_trailing_newline(value):
    with pytest.raises(InvalidCalendar):
        vDuration.from_ical(value)


@pytest.mark.parametrize("value", ["12:00:00\n", "07:00:00Z\n"])
def test_vTime_parse_jcal_value_rejects_trailing_newline(value):
    with pytest.raises(JCalParsingError):
        vTime.parse_jcal_value(value)


@pytest.mark.parametrize("value", ["+01:00\n", "-05:00\n", "+02:30:40\n"])
def test_vUTCOffset_from_jcal_rejects_trailing_newline(value):
    with pytest.raises(JCalParsingError):
        vUTCOffset.from_jcal(["tzoffsetto", {}, "utc-offset", value])


def test_valid_values_still_parse():
    """The anchor change must not reject otherwise valid values."""
    assert vDuration.from_ical("P1D")
    assert vTime.parse_jcal_value("12:00:00")
    assert vUTCOffset.from_jcal(["tzoffsetto", {}, "utc-offset", "+01:00"])
