"""Tests for jCal running on all ics files."""

import json
from datetime import datetime
from pprint import pprint

import pytest

from icalendar.cal.alarm import Alarm
from icalendar.timezone.tzid import is_utc

# Some source calendars use globally unique TZIDs, so issuing the
# GloballyUniqueTZIDGuessed warning is the expected behavior under test.
pytestmark = pytest.mark.filterwarnings(
    "ignore::icalendar.error.GloballyUniqueTZIDGuessed"
)


def test_to_jcal_can_be_json_serialized(source_file):
    """Check that all calendars can be converted to JCAL and serialized to JSON."""
    jcal = source_file.to_jcal()
    s = json.dumps(jcal)
    assert s


def test_trigger(tzp):
    """Check jCal loading of TRIGGER."""
    alarm = Alarm()
    alarm.TRIGGER = tzp.localize_utc(datetime(2022, 1, 1))
    assert is_utc(alarm.TRIGGER)
    jcal = alarm.to_jcal()
    pprint(jcal)
    alarm2 = Alarm.from_jcal(jcal)
    assert alarm2.TRIGGER.replace(tzinfo=None) == datetime(2022, 1, 1)
    assert is_utc(alarm2.TRIGGER)


def test_trigger_from_example(events):
    """Check jCal loading of TRIGGER."""
    alarm: Alarm = events.rfc_9074_example_proximity.subcomponents[0]
    print(alarm["TRIGGER"])
    jcal = alarm.to_jcal()
    pprint(jcal)
    alarm2 = Alarm.from_jcal(jcal)
    assert alarm2 == alarm
    assert is_utc(alarm2.TRIGGER)
