"""Partial support for RFC 9073: VLOCATION and LOCATION-TYPE."""

import pytest

from icalendar import Calendar, Component, Event, Location, Todo, vCategory, vGeo, vText
from icalendar.cal import Location as CalLocation
from icalendar.parser.ical import ComponentIcalParser
from icalendar.prop import vUnknown


@pytest.mark.parametrize("name", ["VLOCATION", "vlocation"])
def test_location_is_registered(component_factory, name):
    """Both public imports and the parser factory use the dedicated class."""
    assert component_factory.get_component_class(name) is Location is CalLocation


def test_minimal_location():
    """A UID alone is sufficient to represent a location."""
    data = b"BEGIN:VLOCATION\r\nUID:venue@example.com\r\nEND:VLOCATION\r\n"
    location = Component.from_ical(data)
    assert isinstance(location, Location)
    assert location.name == "VLOCATION"
    assert location.uid == "venue@example.com"
    assert isinstance(location["UID"], vText)
    assert location.to_ical() == data


@pytest.mark.parametrize("parent_class", [Event, Todo])
def test_add_multiple_locations(parent_class):
    """Each parent keeps distinct locations and its traditional LOCATION text."""
    parent = parent_class()
    parent.add("location", "Conference venue")
    for uid, name, types in [
        ("hotel@example.com", "Central Hotel", ["hotel", "restaurant"]),
        ("parking@example.com", "Car park", ["parking"]),
    ]:
        location = Location()
        location.add("uid", uid)
        location.add("name", name)
        location.add("location-type", types)
        parent.add_component(location)

    encoded = parent.to_ical()
    assert b"LOCATION-TYPE:hotel,restaurant\r\n" in encoded
    assert encoded.count(b"LOCATION-TYPE:") == 2
    restored = parent_class.from_ical(encoded)
    assert restored["LOCATION"] == "Conference venue"
    assert [location.uid for location in restored.walk("VLOCATION")] == [
        "hotel@example.com",
        "parking@example.com",
    ]
    assert all(isinstance(location, Location) for location in restored.subcomponents)
    assert restored == parent


def test_parse_locations(calendars):
    """Both eager and lazy calendars preserve locations and their properties."""
    calendar = calendars.rfc_9073_locations
    assert [location.uid for location in calendar.walk("VLOCATION")] == [
        "hotel@example.com",
        "parking@example.com",
        "office@example.com",
        "restaurant@example.com",
    ]
    for parent_name in ("VEVENT", "VTODO"):
        locations = calendar.walk(parent_name)[0].subcomponents
        assert len(locations) == 2
        assert all(isinstance(location, Location) for location in locations)

    hotel = calendar.walk("VLOCATION")[0]
    assert isinstance(hotel["NAME"], vText)
    assert hotel["NAME"] == "Hotel Sol, Centro"
    assert hotel["NAME"].params["LANGUAGE"] == "pt-BR"
    assert isinstance(hotel["DESCRIPTION"], vText)
    assert hotel["DESCRIPTION"] == "Recepção no térreo.\nUse a entrada principal."
    assert isinstance(hotel["GEO"], vGeo)
    assert hotel["GEO"].ical_value == (-22.97, -43.23)
    assert isinstance(hotel["LOCATION-TYPE"], vCategory)
    assert list(hotel["LOCATION-TYPE"]) == ["hotel", "restaurant"]
    assert str(hotel["X-ENTRANCE"]) == r"North\, side"
    assert Calendar.from_ical(calendar.to_ical()) == calendar


@pytest.mark.parametrize("format_name", ["jcal", "xcal"])
def test_location_format_conversion(calendars, format_name):
    """The existing jCal and xCal converters preserve locations and text lists."""
    calendar = calendars.rfc_9073_locations
    if format_name == "jcal":
        restored = Calendar.from_jcal(calendar.to_jcal())
    else:
        restored = Calendar.from_xcal(calendar.to_xcal())[0]
    locations = restored.walk("VLOCATION")
    assert len(locations) == 4
    assert all(isinstance(location, Location) for location in locations)
    assert list(locations[0]["LOCATION-TYPE"]) == ["hotel", "restaurant"]
    assert locations[0]["NAME"].params["LANGUAGE"] == "pt-BR"
    assert locations[0]["GEO"].ical_value == (-22.97, -43.23)
    assert restored == calendar


@pytest.mark.parametrize(
    ("component_class", "property_name"),
    [(Location, "LOCATION-TYPE"), (Event, "CATEGORIES")],
)
@pytest.mark.parametrize("value_parameter", ["", ";VALUE=TEXT"])
@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("hotel", ["hotel"]),
        ("hotel,restaurant", ["hotel", "restaurant"]),
        (r"hotel\,restaurant,office", ["hotel,restaurant", "office"]),
        (r"room\\,restaurant", ["room\\", "restaurant"]),
        (
            r"café\,terrace,http://example.com/type",
            ["café,terrace", "http://example.com/type"],
        ),
        ("hotel,\r\n restaurant", ["hotel", "restaurant"]),
    ],
)
def test_parse_text_lists(
    component_class, property_name, value_parameter, raw_value, expected
):
    """Split raw text before unescaping, including folded lines and parameters."""
    source = (
        f"BEGIN:{component_class.name}\r\n"
        "UID:place@example.com\r\n"
        f'{property_name}{value_parameter};X-REF="https://example.com/a:b":{raw_value}\r\n'
        f"END:{component_class.name}\r\n"
    )
    component = component_class.from_ical(source)
    value = component[property_name]
    assert isinstance(value, vCategory)
    assert list(value) == expected
    assert value.params["X-REF"] == "https://example.com/a:b"
    restored = component_class.from_ical(component.to_ical())
    assert list(restored[property_name]) == expected
    assert restored[property_name].params == value.params


def test_existing_categories_hook(component_factory, types_factory):
    """Existing parser overrides keep their signature and only handle CATEGORIES."""

    class ExistingParser(ComponentIcalParser):
        def handle_categories(self, params, vals, line):
            params["X-HANDLED"] = "yes"
            return super().handle_categories(params, vals, line)

    source = (
        "BEGIN:VEVENT\r\n"
        "CATEGORIES:Work,Personal\\,Urgent\r\n"
        "BEGIN:VLOCATION\r\n"
        "UID:place@example.com\r\n"
        "LOCATION-TYPE:hotel,restaurant\r\n"
        "END:VLOCATION\r\n"
        "END:VEVENT\r\n"
    )
    event = ExistingParser(source, component_factory, types_factory).parse()[0]
    assert list(event["CATEGORIES"]) == ["Work", "Personal,Urgent"]
    assert event["CATEGORIES"].params["X-HANDLED"] == "yes"
    location_types = event.subcomponents[0]["LOCATION-TYPE"]
    assert list(location_types) == ["hotel", "restaurant"]
    assert "X-HANDLED" not in location_types.params


@pytest.mark.parametrize(
    ("component_class", "property_name"),
    [(Location, "LOCATION-TYPE"), (Event, "CATEGORIES")],
)
@pytest.mark.parametrize("value_parameter", ["", ";VALUE=TEXT"])
def test_text_list_subclasses(
    component_factory, types_factory, component_class, property_name, value_parameter
):
    """Custom text-list types retain escaped commas, parameters and their class."""

    class CustomCategory(vCategory):
        pass

    types_factory.types_map = types_factory.types_map.copy()
    types_factory["custom-categories"] = CustomCategory
    types_factory.types_map[property_name] = "custom-categories"
    source = (
        f"BEGIN:{component_class.name}\r\n"
        f"{property_name}{value_parameter};X-NOTE=custom:hotel,restaurant\\,terrace\r\n"
        f"END:{component_class.name}\r\n"
    )
    component = ComponentIcalParser(source, component_factory, types_factory).parse()[0]
    value = component[property_name]
    assert isinstance(value, CustomCategory)
    assert list(value) == ["hotel", "restaurant,terrace"]
    assert value.params["X-NOTE"] == "custom"
    restored = ComponentIcalParser(
        component.to_ical(), component_factory, types_factory
    ).parse()[0]
    assert isinstance(restored[property_name], CustomCategory)
    assert list(restored[property_name]) == list(value)
    assert restored[property_name].params == value.params


@pytest.mark.parametrize("types", ["hotel", ["hotel", "restaurant"]])
def test_add_location_types(types):
    """A string or list produces one property with the appropriate values."""
    location = Location()
    location.add("location-type", types, parameters={"VALUE": "TEXT"})
    encoded = location.to_ical()
    expected = [types] if isinstance(types, str) else types
    assert encoded.count(b"LOCATION-TYPE;") == 1
    assert list(Location.from_ical(encoded)["LOCATION-TYPE"]) == expected


@pytest.mark.parametrize(
    ("component_class", "property_name"),
    [(Location, "LOCATION-TYPE"), (Event, "CATEGORIES")],
)
def test_unknown_value_is_preserved(component_class, property_name):
    """An explicit UNKNOWN value must bypass text-list processing."""
    raw_value = r"hotel\,restaurant,office\nannex"
    source = (
        f"BEGIN:{component_class.name}\r\n"
        f"{property_name};VALUE=UNKNOWN:{raw_value}\r\n"
        f"END:{component_class.name}\r\n"
    )
    component = component_class.from_ical(source)
    assert isinstance(component[property_name], vUnknown)
    assert str(component[property_name]) == raw_value
    assert component.to_ical() == source.encode()


@pytest.mark.parametrize("component_class", [Location, Calendar])
def test_name_is_text(component_class):
    """NAME is decoded as TEXT, including its use in RFC 7986 calendars."""
    source = (
        f"BEGIN:{component_class.name}\r\n"
        "NAME;LANGUAGE=pt-BR:Hotel Sol\\, Centro\r\n"
        f"END:{component_class.name}\r\n"
    )
    component = component_class.from_ical(source)
    assert isinstance(component["NAME"], vText)
    assert component["NAME"] == "Hotel Sol, Centro"
    assert component["NAME"].params["LANGUAGE"] == "pt-BR"


def test_location_text_round_trip():
    """Text escaping, Unicode and line folding use the existing serializers."""
    location = Location()
    location.add("uid", "venue@example.com")
    location.add("name", "São Paulo, Centro " * 10)
    location.add("description", "Entrance; east\\west\nSecond floor")
    location.add("geo", (-23.55, -46.63))
    location.add("location-type", ["café,terrace", "room\\A"])
    encoded = location.to_ical()
    assert b"\r\n " in encoded
    restored = Location.from_ical(encoded)
    assert restored["NAME"] == location["NAME"]
    assert restored["DESCRIPTION"] == location["DESCRIPTION"]
    assert list(restored["LOCATION-TYPE"]) == ["café,terrace", "room\\A"]
    assert restored == location


def test_invalid_geo():
    """Malformed coordinates follow the existing vGeo error handling."""
    with pytest.raises(ValueError, match="float;float"):
        Location.from_ical("BEGIN:VLOCATION\r\nGEO:invalid\r\nEND:VLOCATION\r\n")
