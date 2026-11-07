"""Resolve custom timezones before parsing dates in jCal and xCal."""

import json
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from icalendar import Calendar, Component, Event, config
from icalendar.error import JCalParsingError, XCalParsingError

TZID = "Custom/Issue1926"
FIXED_TZID = "Custom/Issue1926Fixed"


@pytest.fixture(params=["jcal", "xml"])
def calendar_input(request, tzp):
    """Read native input with a fresh timezone cache for every test."""
    # The tzp fixture has module scope; each case needs an empty cache.
    tzp.use(tzp.name)
    # The calendars fixture would parse the input and populate the cache.
    path = Path(__file__).parent / "calendars" / f"issue_1926_timezones.{request.param}"
    data = path.read_bytes()
    yield (
        json.loads(data)
        if request.param == "jcal"
        else config.parse_xml(BytesIO(data)).getroot()
    )
    tzp.use(tzp.name)


def _children(data):
    return (
        data[2] if isinstance(data, list) else data.find("{*}vcalendar/{*}components")
    )


def _parse(data):
    if isinstance(data, (str, list)):
        return Calendar.from_jcal(data)
    return Calendar.from_xcal(data)[0]


def _serialize(data):
    return json.dumps(data) if isinstance(data, list) else ET.tostring(data)


@pytest.mark.parametrize("position", [0, 1, 3], ids=["before", "between", "after"])
def test_timezone_order_does_not_change_dates(calendar_input, tzp, position):
    """Resolve both custom timezones without a preceding from_ical call."""
    children = _children(calendar_input)
    events, timezones = list(children[:3]), list(children[3:])
    children[:] = events[:position] + timezones + events[position:]
    assert tzp.timezone(TZID) is None
    assert tzp.timezone(FIXED_TZID) is None

    calendar = _parse(calendar_input)

    expected = [
        (timedelta(hours=1), datetime(2025, 1, 1, 8, tzinfo=timezone.utc)),
        (timedelta(hours=2), datetime(2025, 7, 1, 7, tzinfo=timezone.utc)),
        (
            timedelta(hours=5, minutes=45),
            datetime(2025, 7, 1, 3, 15, tzinfo=timezone.utc),
        ),
    ]
    for event, (offset, utc_start) in zip(calendar.events, expected, strict=True):
        assert event.start.utcoffset() == offset
        assert event.end.utcoffset() == offset
        assert event.start.astimezone(timezone.utc) == utc_start
        assert event.end.astimezone(timezone.utc) == utc_start + timedelta(hours=1)


@pytest.mark.parametrize("position", [0, 1, 3], ids=["before", "between", "after"])
def test_parsing_preserves_input_and_component_order(calendar_input, position):
    """Timezone priority changes neither the input nor the returned order."""
    children = _children(calendar_input)
    events, timezones = list(children[:3]), list(children[3:])
    children[:] = events[:position] + timezones + events[position:]
    original = _serialize(calendar_input)

    calendar = _parse(calendar_input)

    assert _serialize(calendar_input) == original
    assert [component.name for component in calendar.subcomponents] == (
        ["VEVENT"] * position + ["VTIMEZONE"] * 2 + ["VEVENT"] * (3 - position)
    )
    assert [event.uid for event in calendar.events] == ["winter", "summer", "fixed"]
    assert [str(tz["TZID"]) for tz in calendar.timezones] == [TZID, FIXED_TZID]


def test_timezone_parameters_are_preserved(calendar_input):
    """Keep the original TZID on event date properties."""
    calendar = _parse(calendar_input)

    for event, tzid in zip(calendar.events, [TZID, TZID, FIXED_TZID], strict=True):
        assert event["DTSTART"].params["TZID"] == tzid
        assert event["DTEND"].params["TZID"] == tzid


def test_rdates_span_daylight_saving_time(calendar_input):
    """Resolve recurrence dates on both sides of a daylight saving transition."""
    calendar = _parse(calendar_input)
    rdate = calendar.events[0]["RDATE"]

    assert [value.dt.utcoffset() for value in rdate.dts] == [
        timedelta(hours=1),
        timedelta(hours=2),
    ]
    assert rdate.params["TZID"] == TZID
    assert [value.dt.astimezone(timezone.utc) for value in rdate.dts] == [
        datetime(2025, 1, 8, 8, tzinfo=timezone.utc),
        datetime(2025, 7, 8, 7, tzinfo=timezone.utc),
    ]


def test_serialized_input_resolves_timezones(calendar_input):
    """JSON strings and XML bytes use the same timezone preparation."""
    calendar = _parse(_serialize(calendar_input))
    assert calendar.events[0].start.utcoffset() == timedelta(hours=1)
    assert calendar.events[1].start.utcoffset() == timedelta(hours=2)


def test_standalone_timezone_is_registered(calendar_input, tzp):
    """A fully parsed timezone is available to subsequent component parsing."""
    children = _children(calendar_input)
    timezone_component = _parse(children[3])
    assert timezone_component.name == "VTIMEZONE"
    assert tzp.timezone(TZID) is not None
    assert _parse(children[0]).start.utcoffset() == timedelta(hours=1)


def test_timezone_without_tzid_is_not_registered(calendar_input):
    """Incomplete timezones without TZID remain parseable, as in iCalendar."""
    children = _children(calendar_input)
    timezone_component = children[4]
    if isinstance(timezone_component, list):
        timezone_component[1] = []
    else:
        properties = timezone_component.find("{*}properties")
        properties.remove(properties.find("{*}tzid"))
    children[:] = [timezone_component]
    assert "TZID" not in _parse(calendar_input).timezones[0]


def test_timezone_error_keeps_original_location(calendar_input):
    """Processing a late timezone first must preserve its original error path."""
    timezone_component = _children(calendar_input)[4]
    if isinstance(calendar_input, list):
        timezone_component[2][0][0] = "invalid name"
        with pytest.raises(JCalParsingError) as error:
            _parse(calendar_input)
        assert error.value.path == [2, 4, 2, 0, 0]
    else:
        timezone_component.find("{*}components/{*}standard").tag = "invalid name"
        with pytest.raises(XCalParsingError) as error:
            _parse(calendar_input)
        assert error.value.element.get_xpath() == (
            "/icalendar/vcalendar[1]/components[1]/vtimezone[2]/components[1]"
            "/invalid name[1]"
        )


class ComponentWithDefaults(Component):
    """A registered component whose constructor supplies a default child."""

    name = "X-ISSUE-1926-DEFAULTS"

    def __init__(self):
        super().__init__()
        self.default_event = Event()
        self.default_event.add("uid", "default")
        self.add_component(self.default_event)
        self.original_subcomponents = self.subcomponents


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
@pytest.mark.parametrize("uids", [[], ["first", "second"]], ids=["empty", "children"])
def test_preserve_constructor_subcomponents(format_name, uids):
    """Append parsed children without replacing a custom component's defaults."""
    Calendar.register(ComponentWithDefaults)
    component_name = ComponentWithDefaults.name.lower()
    if format_name == "jcal":
        children = [["vevent", [["uid", {}, "text", uid]], []] for uid in uids]
        data = ["vcalendar", [], [[component_name, [], children]]]
    else:
        data = ET.Element("vcalendar")
        container = ET.SubElement(ET.SubElement(data, "components"), component_name)
        children = ET.SubElement(container, "components")
        for uid in uids:
            event = ET.SubElement(children, "vevent")
            properties = ET.SubElement(event, "properties")
            ET.SubElement(ET.SubElement(properties, "uid"), "text").text = uid

    component = _parse(data).subcomponents[0]

    assert isinstance(component, ComponentWithDefaults)
    assert component.subcomponents is component.original_subcomponents
    assert component.subcomponents[0] is component.default_event
    assert [event.uid for event in component.subcomponents] == ["default", *uids]
