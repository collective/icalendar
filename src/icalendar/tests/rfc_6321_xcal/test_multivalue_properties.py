"""Multi-value properties in xCal.

These tests use the example file `rfc_6321_multivalue_properties_xcal.xml`
to check that the multi-value properties of RFC 6321 Section 3.4.1.1

- CATEGORIES
- RESOURCES
- FREEBUSY
- EXDATE
- RDATE

are parsed from xCal and serialized back into xCal, both with a single
value and with several values.

Issue: #2027
"""

from datetime import datetime, timezone
from xml.etree.ElementTree import Element, tostring

from icalendar.cal.component import Component
from icalendar.prop import vText

NS = "{urn:ietf:params:xml:ns:icalendar-2.0}"

EXDATE_MULTIPLE = [
    datetime(2026, 11, 2, 9, 0, tzinfo=timezone.utc),
    datetime(2026, 11, 9, 9, 0, tzinfo=timezone.utc),
]
RDATE = datetime(2026, 12, 1, 9, 0, tzinfo=timezone.utc)
FREEBUSY_MULTIPLE = [
    (
        datetime(2026, 10, 26, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 26, 10, 0, tzinfo=timezone.utc),
    ),
    (
        datetime(2026, 10, 26, 13, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 26, 14, 0, tzinfo=timezone.utc),
    ),
]
FREEBUSY_SINGLE = [
    (
        datetime(2026, 10, 27, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 27, 10, 0, tzinfo=timezone.utc),
    ),
]


def to_xcal_string(component: Component) -> str:
    """Serialize a component to an xCal string."""
    root = Element("icalendar")
    component.to_xcal(root)
    return tostring(root, encoding="unicode")


def resource_values(resources) -> list:
    """RESOURCES values: a list for several values, a vText for one value."""
    if isinstance(resources, list):
        return list(resources)
    return [resources]


def period_values(periods) -> list:
    """FREEBUSY values as (start, end) tuples."""
    if not isinstance(periods, list):
        periods = [periods]  # a single value
    return [(p.start, p.end) for p in periods]


def test_the_example_file_is_used(calendars):
    """The example calendar is parsed from the XML file."""
    calendar = calendars.rfc_6321_multivalue_properties_xcal
    assert len(calendar.subcomponents) == 4


def test_categories_multiple_values(calendars):
    """CATEGORIES with two values is parsed into a list of two entries."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[0]
    categories = event["CATEGORIES"]
    assert categories.cats == [vText("Work"), vText("Meeting")]


def test_resources_multiple_values(calendars):
    """RESOURCES with two values is parsed into a list of two entries."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[0]
    resources = event["RESOURCES"]
    assert resource_values(resources) == [vText("Projector"), vText("Whiteboard")]


def test_exdate_multiple_values(calendars):
    """EXDATE with two values is parsed into a list of two entries."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[0]
    exdate = event["EXDATE"]
    assert [d.dt for d in exdate.dts] == EXDATE_MULTIPLE


def test_rdate_single_value(calendars):
    """RDATE with one value is parsed."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[0]
    rdate = event["RDATE"]
    assert [d.dt for d in rdate.dts] == [RDATE]


def test_single_values_categories(calendars):
    """CATEGORIES with one value is parsed."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[1]
    assert event["CATEGORIES"].cats == [vText("Work")]


def test_single_values_resources(calendars):
    """RESOURCES with one value is parsed."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[1]
    assert resource_values(event["RESOURCES"]) == [vText("Projector")]


def test_single_values_exdate(calendars):
    """EXDATE with one value is parsed."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[1]
    assert [d.dt for d in event["EXDATE"].dts] == EXDATE_MULTIPLE[:1]


def test_single_values_rdate(calendars):
    """RDATE with one value is parsed."""
    event = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[1]
    assert [d.dt for d in event["RDATE"].dts] == [RDATE]


def test_freebusy_multiple_values(calendars):
    """FREEBUSY with two periods is parsed into a list of two entries."""
    freebusy = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[2]
    periods = freebusy["FREEBUSY"]
    assert period_values(periods) == FREEBUSY_MULTIPLE


def test_freebusy_single_value(calendars):
    """FREEBUSY with one period is parsed."""
    freebusy = calendars.rfc_6321_multivalue_properties_xcal.subcomponents[3]
    periods = freebusy["FREEBUSY"]
    assert period_values(periods) == FREEBUSY_SINGLE


def test_xcal_serialization_of_multiple_values(calendars):
    """The multi-value properties serialize into XML elements.

    CATEGORIES, RESOURCES, EXDATE, RDATE and FREEBUSY serialize so that
    they can be parsed back into the same values.
    """
    calendar = calendars.rfc_6321_multivalue_properties_xcal
    xcal_string = to_xcal_string(calendar)
    parsed = Component.from_xcal(xcal_string.encode())[0]
    events = [c for c in parsed.subcomponents if c.name == "VEVENT"]
    multiple, single = events[0], events[1]
    # several values
    assert multiple["CATEGORIES"].cats == [vText("Work"), vText("Meeting")]
    assert resource_values(multiple["RESOURCES"]) == [
        vText("Projector"),
        vText("Whiteboard"),
    ]
    assert [d.dt for d in multiple["EXDATE"].dts] == EXDATE_MULTIPLE
    assert [d.dt for d in multiple["RDATE"].dts] == [RDATE]
    # a single value
    assert single["CATEGORIES"].cats == [vText("Work")]
    assert resource_values(single["RESOURCES"]) == [vText("Projector")]
    assert [d.dt for d in single["EXDATE"].dts] == EXDATE_MULTIPLE[:1]
    freebusy = [c for c in parsed.subcomponents if c.name == "VFREEBUSY"]
    assert period_values(freebusy[0]["FREEBUSY"]) == FREEBUSY_MULTIPLE
    assert period_values(freebusy[1]["FREEBUSY"]) == FREEBUSY_SINGLE
    # the XML uses the value elements of RFC 6321, not a comma-separated string
    assert "<categories><text>Work</text><text>Meeting</text></categories>" in (
        xcal_string
    )


def test_exdate_and_rdate_use_date_time_value_elements(calendars):
    """EXDATE and RDATE serialize into <date-time> value elements."""
    calendar = calendars.rfc_6321_multivalue_properties_xcal
    xcal_string = to_xcal_string(calendar)
    assert "<exdate><date-time>2026-11-02T09:00:00Z</date-time>" in xcal_string
    assert "<rdate><date-time>2026-12-01T09:00:00Z</date-time></rdate>" in xcal_string


RESOURCES_MULTIPLE = [vText("Projector"), vText("Whiteboard")]


def calendar_with_resources() -> Component:
    """A calendar with one event with several RESOURCES values."""
    from icalendar import Calendar, Event

    calendar = Calendar.new()
    event = Event()
    event.add("RESOURCES", RESOURCES_MULTIPLE)
    calendar.add_component(event)
    return calendar


def test_resources_serialize_to_ical():
    """RESOURCES values survive an iCal serialization round-trip.

    RFC 5545 allows RESOURCES to occur several times, and this is how
    a list of values is serialized: one property occurrence per value.
    """
    calendar = calendar_with_resources()
    ical = calendar.to_ical()
    parsed = Component.from_ical(ical)
    event = parsed.walk("VEVENT")[0]
    assert resource_values(event["RESOURCES"]) == RESOURCES_MULTIPLE


def test_resources_serialize_to_xcal():
    """RESOURCES values survive an xCal serialization round-trip.

    Each value is serialized into its own <resources> property element
    with one <text> value element per value.
    """
    calendar = calendar_with_resources()
    xcal_string = to_xcal_string(calendar)
    parsed = Component.from_xcal(xcal_string.encode())[0]
    event = parsed.walk("VEVENT")[0]
    assert resource_values(event["RESOURCES"]) == RESOURCES_MULTIPLE
    assert (
        "<resources><text>Projector</text></resources>"
        "<resources><text>Whiteboard</text></resources>" in xcal_string
    )


def test_resources_serialize_to_jcal():
    """RESOURCES values survive a jCal serialization round-trip.

    Each value is serialized as a separate jCal property array, see
    RFC 7265 Section 3.6.1 on multi-valued properties.
    """
    calendar = calendar_with_resources()
    jcal = calendar.to_jcal()
    parsed = Component.from_jcal(jcal)
    event = parsed.walk("VEVENT")[0]
    assert resource_values(event["RESOURCES"]) == RESOURCES_MULTIPLE
    # the event's properties contain one "resources" entry per value
    event_jcal = [comp for comp in jcal[-1] if comp[0] == "vevent"][0]
    resources_entries = [prop for prop in event_jcal[1] if prop[0] == "resources"]
    assert [entry[3] for entry in resources_entries] == ["Projector", "Whiteboard"]
