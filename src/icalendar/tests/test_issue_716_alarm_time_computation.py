"""Test the alarm time computation."""

from datetime import date, datetime, timedelta, timezone

import pytest

from icalendar.alarms import Alarms, IncompleteAlarmInformation
from icalendar.cal import Alarm, InvalidCalendar
from icalendar.prop import vDatetime
from icalendar.tools import normalize_pytz

UTC = timezone.utc
EXAMPLE_TRIGGER = datetime(1997, 3, 17, 13, 30, tzinfo=UTC)


def test_absolute_alarm_time_rfc_example(alarms):
    """Check that the absolute alarm is recognized.

    The following example is for a "VALARM" calendar component
    that specifies an audio alarm that will sound at a precise time
    and repeat 4 more times at 15-minute intervals:
    """
    a = Alarms(alarms.rfc_5545_absolute_alarm_example)
    times = a.times
    assert len(times) == 5
    for i, t in enumerate(times):
        assert t.trigger == EXAMPLE_TRIGGER + timedelta(minutes=15 * i)


alarm_1 = Alarm()
alarm_1.add("TRIGGER", EXAMPLE_TRIGGER)
alarm_2 = Alarm()
alarm_2["TRIGGER"] = vDatetime(EXAMPLE_TRIGGER)

@pytest.mark.parametrize(
    "alarm",
    [
        alarm_1, alarm_2
    ]
)
def test_absolute_alarm_time_with_vDatetime(alarm):
    """Check that the absolute alarm is recognized.

    The following example is for a "VALARM" calendar component
    that specifies an audio alarm that will sound at a precise time
    and repeat 4 more times at 15-minute intervals:
    """
    a = Alarms(alarm)
    times = a.times
    assert len(times) == 1
    assert times[0].trigger == EXAMPLE_TRIGGER


def test_repeat_absent():
    """Test the absence of REPEAT."""
    assert Alarm().REPEAT == 0


def test_repeat_number():
    """Test the absence of REPEAT."""
    assert Alarm({"REPEAT": 10}).REPEAT == 10


def test_set_REPEAT():
    """Check setting the value."""
    a = Alarm()
    a.REPEAT = 10
    assert a.REPEAT == 10


def test_set_REPEAT_twice():
    """Check setting the value."""
    a = Alarm()
    a.REPEAT = 10
    a.REPEAT = 20
    assert a.REPEAT == 20


def test_add_REPEAT():
    """Check setting the value."""
    a = Alarm()
    a.add("REPEAT", 10)
    assert a.REPEAT == 10


def test_invalid_repeat_value():
    """Check setting the value."""
    a = Alarm()
    with pytest.raises(ValueError):
        a.REPEAT = "asd"
    a["REPEAT"] = "asd"
    with pytest.raises(InvalidCalendar):
        a.REPEAT  # noqa: B018


def test_alarm_to_string():
    a = Alarm()
    a.REPEAT = 11
    assert a.to_ical() == b"BEGIN:VALARM\r\nREPEAT:11\r\nEND:VALARM\r\n"


def test_alarm_has_only_one_of_repeat_or_duration():
    """This is an edge case and we should ignore the repetition."""
    pytest.skip("TODO")


@pytest.fixture(params=[(0, timedelta(minutes=-30)), (1, timedelta(minutes=-25))])
def alarm_before_start(calendars, request):
    """An example alarm relative to the start of a component."""
    index, td = request.param
    alarm = calendars.alarm_etar_future.subcomponents[-1].subcomponents[index]
    assert isinstance(alarm, Alarm)
    assert alarm.get("TRIGGER").dt == td
    alarm.test_td = td
    return alarm


def test_cannot_compute_relative_alarm_without_start(alarm_before_start):
    """We have an alarm without a start of a component."""
    with pytest.raises(IncompleteAlarmInformation) as e:
        Alarms(alarm_before_start).times  # noqa: B018
    assert e.value.args[0] == f"Use {Alarms.__name__}.{Alarms.set_start.__name__} because at least one alarm is relative to the start of a component."


@pytest.mark.parametrize(
    ("dtstart", "timezone", "trigger"),
    [
        (datetime(2024, 10, 29, 13, 10), "UTC", datetime(2024, 10, 29, 13, 10, tzinfo=UTC)),
        (date(2024, 11, 16), None, datetime(2024, 11, 16, 0, 0)),
        (datetime(2024, 10, 29, 13, 10), "Asia/Singapore", datetime(2024, 10, 29, 5, 10, tzinfo=UTC)),
        (datetime(2024, 10, 29, 13, 20), None, datetime(2024, 10, 29, 13, 20)),
    ]
)
def test_can_complete_relative_calculation_if_a_start_is_given(alarm_before_start, dtstart, timezone, trigger, tzp):
    """The start is given and required."""
    start = (dtstart if timezone is None else tzp.localize(dtstart, timezone))
    alarms = Alarms(alarm_before_start)
    alarms.set_start(start)
    assert len(alarms.times) == 1
    time = alarms.times[0]
    expected_trigger = normalize_pytz(trigger + alarm_before_start.test_td)
    assert time.trigger == expected_trigger


@pytest.mark.parametrize("dtstart", [date(1998, 10, 1), date(2023, 12, 31)])
def test_start_as_date_with_delta_as_date_stays_date(alarms, dtstart):
    """If we have an alarm with a day delta and the event is a day event, we should stay as a date."""
    a = Alarms(alarms.start_date)
    a.set_start(dtstart)
    assert len(a.times) == 1
    assert a.times[0].trigger == dtstart - timedelta(days=2)


def test_cannot_compute_relative_alarm_without_end(alarms):
    """We have an alarm without an end of a component."""
    with pytest.raises(IncompleteAlarmInformation) as e:
        Alarms(alarms.rfc_5545_end).times  # noqa: B018
    assert e.value.args[0] == f"Use {Alarms.__name__}.{Alarms.set_end.__name__} because at least one alarm is relative to the end of a component."


@pytest.mark.parametrize(
    ("dtend", "timezone", "trigger"),
    [
        (datetime(2024, 10, 29, 13, 10), "UTC", datetime(2024, 10, 29, 13, 10, tzinfo=UTC)),
        (date(2024, 11, 16), None, date(2024, 11, 16)),
        (datetime(2024, 10, 29, 13, 10), "Asia/Singapore", datetime(2024, 10, 29, 5, 10, tzinfo=UTC)),
        (datetime(2024, 10, 29, 13, 20), None, datetime(2024, 10, 29, 13, 20)),
    ]
)
def test_can_complete_relative_calculation_if_a_start_is_given(alarms, dtend, timezone, trigger, tzp):
    """The start is given and required."""
    start = (dtend if timezone is None else tzp.localize(dtend, timezone))
    alarms = Alarms(alarms.rfc_5545_end)
    alarms.set_end(start)
    assert len(alarms.times) == 1
    time = alarms.times[0]
    expected_trigger = normalize_pytz(trigger - timedelta(days=2))
    assert time.trigger == expected_trigger


@pytest.mark.parametrize("dtend", [date(1998, 10, 1), date(2023, 12, 31)])
def test_end_as_date_with_delta_as_date_stays_date(alarms, dtend):
    """If we have an alarm with a day delta and the event is a day event, we should stay as a date."""
    a = Alarms(alarms.rfc_5545_end)
    a.set_end(dtend)
    assert len(a.times) == 1
    assert a.times[0].trigger == dtend - timedelta(days=2)



def test_add_multiple_alarms(alarms):
    """We can add multiple alarms."""
    a = Alarms()
    a.add_alarm(alarms.start_date)
    a.add_alarm(alarms.rfc_5545_end)
    a.add_alarm(alarms.rfc_5545_absolute_alarm_example)
    with pytest.raises(IncompleteAlarmInformation):
        a.times  # noqa: B018
    a.set_start(datetime(2012, 3, 5))
    with pytest.raises(IncompleteAlarmInformation):
        a.times  # noqa: B018
    a.set_end(datetime(2012, 3, 5))
    assert len(a.times) == 7


def test_alarms_from_event_have_right_times(calendars):
    """We can collect from an event."""
    event = calendars.alarm_etar_future.subcomponents[-1]
    a = Alarms(event)
    assert len(a.times) == 3
    assert a.times[0].parent == event


def test_cannot_set_the_event_twice(calendars):
    """We cannot set an event twice. This make the state ambiguous."""
    event = calendars.alarm_etar_future.subcomponents[-1]
    a = Alarms()
    a.add_component(event)
    a.add_component(event)  # same component is ok
    with pytest.raises(ValueError):
        a.add_component(calendars.alarm_google_future.subcomponents[-1])


def test_alarms_from_calendar():
    pytest.skip("TODO")
