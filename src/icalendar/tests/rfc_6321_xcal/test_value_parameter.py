"""The VALUE parameter deserves special handling.

When converting from xCal into
iCalendar, the appropriate "VALUE" property parameter MUST be
included in the iCalendar property if the value type is not the
default value type for that property.

In these tests, we combine rules from different RFCs:

> If the property has no "VALUE" parameter and has no default value
> type, "unknown" is used.
> - https://datatracker.ietf.org/doc/html/rfc7265#section-3.5.1

Conclusions:

- (CASE 1) The UNKNOWN VALUE parameter must be preserved when converting from xCal to iCalendar and back.


> When converting from xCal into
> iCalendar, the appropriate "VALUE" property parameter MUST be
> included in the iCalendar property if the value type is not the
> default value type for that property.
> - https://datatracker.ietf.org/doc/html/rfc6321#section-3.5.1

Conclusions:

- The value parameter must be set on the property
  - (CASE 2) if it does not have a default VALUE
  - (CASE 3) if the VALUE deviates from the default VALUE for that property
- (CASE 4) The VALUE parameter must be omitted if it is a default type

> This property parameter is not mapped to an xCal XML
> element.  Instead, the value type is handled by having different XML
> elements for each value, and these appear inside of property
> elements.
> Thus, when converting from iCalendar to xCal, any "VALUE"
> property parameters are skipped.
> - https://datatracker.ietf.org/doc/html/rfc6321#section-3.5.1

Conclusions:

- (CASE 5) The VALUE parameter is not considered at all. The value is important.
  With the value being important, we can omit that parameter and just
  focus on assigning the correct value.
  That is probably an easy decision for now. It implies that the
  VALUE parameter does not round-trip for custom property values.
  If required, future issues can be opened and specify this, so it
  is done with a use-case and now with speculation.

(CASE 5) Will be implemented so that custom types are preserved during round-trip.
"""

from datetime import date
from pprint import pprint

import pytest

from icalendar import prop
from icalendar.cal.component import Component
from icalendar.cal.event import Event
from icalendar.prop import VPROPERTY, vDate, vText, vUri
from icalendar.prop.factory import TypesFactory
from icalendar.prop.uid import vUid
from icalendar.prop.unknown import vUnknown
from icalendar.prop.xml_reference import vXmlReference
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal_list


@pytest.mark.parametrize("prop", ["x-prop", "summary"])
def test_case_1_unknown_is_preserved_from_xcal(prop):
    """The UNKNOWN VALUE parameter must be preserved when converting from xCal to iCalendar and back."""
    xml = list2xml(
        [
            "vevent",
            [
                "properties",
                [
                    prop,
                    ["unknown", "lalala"],
                ],
            ],
        ]
    )
    event = Event.from_xcal(xml)[0]
    value = event[prop]
    assert isinstance(value, vUnknown)
    assert value.ical_value == "lalala"
    assert "VALUE" in value.params
    assert value.params["VALUE"] == "UNKNOWN"


@pytest.mark.parametrize("prop", ["x-prop", "summary"])
def test_case_1_unknown_is_preserved_to_xcal(prop, comp):
    """The UNKNOWN VALUE parameter must be preserved when converting from xCal to iCalendar and back."""
    comp[prop] = vUnknown("lalala")
    xml = to_xcal_list(comp, wrap=False)
    expected = [
        "vtest",
        [
            "properties",
            [
                prop,
                ["unknown", "lalala"],
            ],
        ],
    ]
    pprint(xml)
    pprint(expected)
    assert xml == expected


@pytest.mark.parametrize("prop", ["x-prop", "summary"])
def test_case_1_unknown_jumps_in_for_custom_types(prop, comp):
    """When parsing, we should set the value parameter accordingly, even if we do not know the type."""
    comp[prop] = vUnknown("lalilu", params={"VALUE": "X-VALUE"})
    xml = to_xcal_list(comp, wrap=False)
    expected = [
        "vtest",
        [
            "properties",
            [
                prop,
                ["x-value", "lalilu"],
            ],
        ],
    ]
    pprint(xml)
    pprint(expected)
    assert xml == expected


@pytest.mark.parametrize("prop", ["x-prop", "summary"])
def test_5_unknown_from_xcal_preserves_round_trip_of_custom_value(prop):
    """A custom property value can be set and vUnkown handles that."""
    xml = list2xml(
        [
            "vevent",
            [
                "properties",
                [
                    prop,
                    ["x-value", "lalala"],
                ],
            ],
        ]
    )
    event = Event.from_xcal(xml)[0]
    value = event[prop]
    assert isinstance(value, vUnknown)
    assert value.ical_value == "lalala"
    assert value.params["VALUE"] == "X-VALUE"


@pytest.mark.parametrize("prop", ["x-prop", "link"])
@pytest.mark.parametrize("value_type", ["x-value", "uri", "uid", "text", "unknown"])
def test_case_2_value_is_set_if_there_is_no_default_from_xcal(prop, value_type):
    """
    LINK is specified in :rfc:`9253` and has no default value type.
    The VALUE parameter must be set.
    X-PROP also has no default value.
    """
    xml = list2xml(
        [
            "vevent",
            [
                "properties",
                [
                    prop,
                    [value_type, "lalala"],
                ],
            ],
        ]
    )
    event = Event.from_xcal(xml)[0]
    value = event[prop]
    assert isinstance(value, (vUnknown, vUri, vUid, vText))
    assert value.ical_value == "lalala"
    assert value_type.upper() == value.params.get("VALUE", value.default_value)


def test_case_3_value_is_set_if_it_deviates_from_default_from_xcal():
    """
    The VALUE parameter must be set if the value type deviates from the default value type for that property.
    """
    comp = Event()
    comp["summary"] = vUnknown("lalala", params={"VALUE": "X-VALUE"})
    comp.start = date(2025, 10, 12)
    xml = to_xcal_list(comp, wrap=False)
    expected = [
        "vevent",
        [
            "properties",
            [
                "summary",
                ["x-value", "lalala"],
            ],
            ["dtstart", ["date", "2025-10-12"]],
        ],
    ]
    pprint(xml)
    pprint(expected)
    assert xml == expected


types_factory = TypesFactory.instance()


# these are the property names with the actual types that are expected
PROP_AND_TYPE = [
    ("ACKNOWLEDGED", prop.vDatetime),
    ("ACTION", prop.vText),
    ("ATTACH", prop.vUri),
    ("ATTENDEE", prop.vCalAddress),
    ("CALSCALE", prop.vText),
    ("CATEGORIES", prop.vCategory),
    ("CLASS", prop.vText),
    ("COMMENT", prop.vText),
    ("COMPLETED", prop.vDatetime),
    ("CONCEPT", prop.vUri),
    ("CONFERENCE", prop.vUri),
    ("CONTACT", prop.vText),
    ("CREATED", prop.vDatetime),
    ("DESCRIPTION", prop.vText),
    ("DTEND", prop.vDatetime),
    ("DTSTAMP", prop.vDatetime),
    ("DTSTART", prop.vDatetime),
    ("DUE", prop.vDatetime),
    ("DURATION", prop.vDuration),
    ("ENCODING", prop.vText),
    ("EXDATE", prop.vDDDLists),
    ("EXRULE", prop.vRecur),
    ("FBTYPE", prop.vText),
    ("FREEBUSY", prop.vPeriod),
    ("GEO", prop.vGeo),
    ("LAST-MODIFIED", prop.vDatetime),
    ("LINK", prop.vUri),
    ("LINKREL", prop.vText),
    ("LOCATION", prop.vText),
    ("MEMBER", prop.vCalAddress),
    ("METHOD", prop.vText),
    ("ORGANIZER", prop.vCalAddress),
    ("PARTSTAT", prop.vText),
    ("PERCENT-COMPLETE", prop.vInt),
    ("PRIORITY", prop.vInt),
    ("PRODID", prop.vText),
    ("PROXIMITY", prop.vText),
    ("RDATE", prop.vDDDLists),
    ("RECURRENCE-ID", prop.vDatetime),
    ("REFID", prop.vText),
    ("RELATED", prop.vText),
    ("RELATED-TO", prop.vText),
    ("RELTYPE", prop.vText),
    ("REPEAT", prop.vInt),
    ("REQUEST-STATUS", prop.vText),
    ("RESOURCES", prop.vText),
    ("ROLE", prop.vText),
    ("RRULE", prop.vRecur),
    ("SEQUENCE", prop.vInt),
    ("SOURCE", prop.vUri),
    ("STATUS", prop.vText),
    ("SUMMARY", prop.vText),
    ("TRANSP", prop.vText),
    ("TRIGGER", prop.vDuration),
    ("TZNAME", prop.vText),
    ("TZOFFSETFROM", prop.vUTCOffset),
    ("TZOFFSETTO", prop.vUTCOffset),
    ("TZURL", prop.vUri),
    ("UID", prop.vText),
    ("URL", prop.vUri),
    ("VERSION", prop.vText),
]


@pytest.mark.parametrize(("property_name", "value_param"), PROP_AND_TYPE)
def test_case_4_value_is_omitted_if_it_is_default_from_xcal(
    property_name, value_param: VPROPERTY, comp
):
    """
    The VALUE parameter must be omitted if it is a default type.
    """
    comp[property_name] = example = value_param.examples()[0]
    example.params.clear()  # We need to start without parameters for this to work
    xml = to_xcal_list(comp, wrap=False)
    xml_prop = xml[1][1]
    assert xml_prop[0] == property_name.lower(), "This is the right property."
    # For this, it is easier to check that there are actually no parameters in XML
    # instead of checking anything else in them
    assert all(value_element[0] != "parameters" for value_element in xml_prop[1:]), (
        f"{property_name} must not have parameters. {xml_prop}"
    )
    compx = Component.from_xcal(list2xml(xml))[0]
    assert compx[property_name] == comp[property_name], "The correct value is used"
    assert "VALUE" not in compx[property_name].params, (
        f"{property_name} {compx[property_name].params} - The VALUE parameter is the default and therefore omitted."
    )


def test_preserve_value_parameter_known_prop_different_type_not_allowed_to_xcal(comp):
    """Special case - what if that value is not allowed."""
    comp["SUMMARY"] = vDate(date(2025, 10, 12))
    xml = to_xcal_list(comp, wrap=False)
    expected = [
        "vtest",
        [
            "properties",
            [
                "summary",
                ["date", "2025-10-12"],
            ],
        ],
    ]
    pprint(xml)
    pprint(expected)
    assert xml == expected


def test_preserve_value_parameter_known_prop_different_type_not_allowed_from_xcal(comp):
    """Similar to the previous test, but now we parse from xCal into iCalendar."""
    xml = list2xml(
        [
            "vtest",
            [
                "properties",
                [
                    "summary",
                    ["date", "2025-10-12"],
                ],
            ],
        ]
    )
    compx = Component.from_xcal(xml)[0]
    assert compx["SUMMARY"].dt == date(2025, 10, 12)


@pytest.mark.parametrize("link_type", [vUid, vUri, vXmlReference])
def test_preserve_value_parameter_known_prop_different_type_extension_round_trip(
    link_type, comp
):
    """
    LINK:
    - VALUE=UID
    - VALUE=URI
    - VALUE=XML-REFERENCE
    https://datatracker.ietf.org/doc/html/rfc9253.html#section-8.2
    """
    comp["LINK"] = link_type.examples()[0]
    xml = to_xcal_list(comp, wrap=False)
    compx = Component.from_xcal(list2xml(xml))[0]
    assert isinstance(compx["LINK"], link_type)
    assert compx["LINK"] == comp["LINK"]
    assert compx["LINK"].params.value is None, (
        "The value parameter in icalendar convention is removed "
        "if it is equal to the default value of the property type."
    )
