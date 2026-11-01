"""Tests for GHSA-qjcq-q7h7-r74v.

A crafted REPEAT value on a VALARM component could exhaust memory or CPU.
See https://github.com/collective/icalendar/security/advisories/GHSA-qjcq-q7h7-r74v
"""

from datetime import datetime, timedelta, timezone

import pytest

import icalendar.config as cfg
from icalendar import Alarm
from icalendar.alarms import Alarms
from icalendar.prop.integer import vInt

UTC = timezone.utc


def _repeating_alarm(repeat: int) -> Alarm:
    a = Alarm()
    a.add("TRIGGER", datetime(2024, 1, 1, 12, 0, tzinfo=UTC))
    a.add("DURATION", timedelta(minutes=5))
    a.add("REPEAT", repeat)
    return a


# vInt RFC 5545 range enforcement


def test_vint_rejects_value_above_max():
    with pytest.raises(ValueError):
        vInt.from_ical("2147483648")


def test_vint_rejects_value_below_min():
    with pytest.raises(ValueError):
        vInt.from_ical("-2147483649")


def test_vint_accepts_boundary_values():
    assert vInt.from_ical("2147483647") == 2147483647
    assert vInt.from_ical("-2147483648") == -2147483648


def test_vint_jcal_rejects_out_of_range():
    with pytest.raises(ValueError):
        vInt.from_jcal(["repeat", {}, "integer", 2147483648])
    with pytest.raises(ValueError):
        vInt.parse_jcal_value(-2147483649)


# Alarm.triggers cap (cal/alarm.py, available since 7.0.0)


@pytest.mark.parametrize("repeat", [999_999_999, 10_001])
def test_alarm_triggers_capped(repeat, monkeypatch):
    monkeypatch.setattr(cfg, "MAX_ALARM_REPEAT", 10_000)
    alarm = _repeating_alarm(repeat)
    assert len(alarm.triggers.absolute) == 10_001


def test_alarm_triggers_small_repeat_unchanged():
    assert len(_repeating_alarm(4).triggers.absolute) == 5


def test_alarm_triggers_negative_repeat():
    assert len(_repeating_alarm(-1).triggers.absolute) == 1


def test_alarm_triggers_cap_disabled(monkeypatch):
    monkeypatch.setattr(cfg, "MAX_ALARM_REPEAT", -1)
    assert len(_repeating_alarm(11_000).triggers.absolute) == 11_001


# Alarms._repeat cap (alarms.py, available since 6.1.0)


@pytest.mark.parametrize("repeat", [999_999_999, 10_001])
def test_alarms_times_capped(repeat, monkeypatch):
    monkeypatch.setattr(cfg, "MAX_ALARM_REPEAT", 10_000)
    assert len(Alarms(_repeating_alarm(repeat)).times) == 10_001


def test_alarms_times_small_repeat_unchanged():
    assert len(Alarms(_repeating_alarm(4)).times) == 5


def test_alarms_times_negative_repeat():
    assert len(Alarms(_repeating_alarm(-1)).times) == 1


def test_alarms_times_cap_disabled(monkeypatch):
    monkeypatch.setattr(cfg, "MAX_ALARM_REPEAT", -1)
    assert len(Alarms(_repeating_alarm(11_000)).times) == 11_001
