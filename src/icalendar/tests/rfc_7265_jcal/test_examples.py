"""Tests for jCal running on all ics files."""

import json
from datetime import datetime
from pprint import pprint

from icalendar import Component
from icalendar.cal.alarm import Alarm
from icalendar.timezone.tzid import is_utc


def test_to_jcal_can_be_json_serialized(ics_file):
    """Check that all calendars can be converted to JCAL and serialized to JSON."""
    jcal = ics_file.to_jcal()
    s = json.dumps(jcal)
    assert s


def test_converting_an_example_back_and_forth_equals_the_original(ics_file: Component):
    """Check that all calendars can be converted to JCAL and back."""
    jcal = ics_file.to_jcal()
    # pprint(jcal)
    component = Component.from_jcal(jcal)
    # print("Got:")
    # print(to_unicode(component.to_ical())[:1000])
    # print("Expected:")
    # print(to_unicode(ics_file.to_ical())[:1000])
    assert component == ics_file


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
