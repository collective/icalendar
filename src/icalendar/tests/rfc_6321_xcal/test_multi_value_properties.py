"""Tests for RFC 6321 Section 3.4.1.1: Multi-valued properties.

RFC 6321 Section 3.4.1.1 specifies:
"Multi-valued properties, such as CATEGORIES or RESOURCES, enclose all their
values in a single property XML element.
For example:
<categories>
  <text>APPOINTMENT</text>
  <text>EDUCATION</text>
</categories>"

Properties covered:
- CATEGORIES
- RESOURCES
- FREEBUSY
- EXDATE
- RDATE
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

from icalendar.cal.calendar import Calendar
from icalendar.cal.event import Event
from icalendar.cal.free_busy import FreeBusy
from icalendar.prop.categories import vCategory
from icalendar.prop.dt.list import vDDDLists
from icalendar.prop.dt.period import vPeriod


def test_multi_value_properties_fixture_parsing_and_roundtrip(calendars):
    """Test parsing multi-valued properties from RFC 6321 xCal fixture and roundtripping."""
    cal = calendars["rfc_6321_multi_value_properties_xcal"]
    assert len(cal.subcomponents) == 2

    # VEVENT verification
    event = [c for c in cal.subcomponents if c.name == "VEVENT"][0]

    # CATEGORIES
    assert isinstance(event["categories"], vCategory)
    assert event["categories"].cats == ["APPOINTMENT", "EDUCATION"]

    # RESOURCES
    assert isinstance(event["resources"], list)
    assert [str(r) for r in event["resources"]] == ["EASEL", "PROJECTOR", "VCR"]

    # EXDATE
    assert isinstance(event["exdate"], vDDDLists)
    assert len(event["exdate"].dts) == 2
    assert event["exdate"].dts[0].dt == datetime(1996, 4, 2, 1, 0, tzinfo=timezone.utc)
    assert event["exdate"].dts[1].dt == datetime(1996, 4, 3, 1, 0, tzinfo=timezone.utc)

    # RDATE
    assert isinstance(event["rdate"], vDDDLists)
    assert len(event["rdate"].dts) == 2
    assert event["rdate"].dts[0].dt == datetime(1996, 4, 4, 1, 0, tzinfo=timezone.utc)
    assert event["rdate"].dts[1].dt == datetime(1996, 4, 5, 1, 0, tzinfo=timezone.utc)

    # VFREEBUSY verification
    vfb = [c for c in cal.subcomponents if c.name == "VFREEBUSY"][0]
    assert isinstance(vfb["freebusy"], list)
    assert len(vfb["freebusy"]) == 2
    assert vfb["freebusy"][0].params.get("FBTYPE") == "BUSY"

    # Serialize to xCal and verify XML structure
    raw_xcal = cal.to_xcal()
    root = ET.fromstring(raw_xcal)
    ns = {"x": "urn:ietf:params:xml:ns:icalendar-2.0"}

    # Assert exactly 1 <categories> tag under vevent properties
    cat_tags = root.findall(".//x:vevent/x:properties/x:categories", ns)
    assert len(cat_tags) == 1
    assert [e.text for e in cat_tags[0].findall("x:text", ns)] == [
        "APPOINTMENT",
        "EDUCATION",
    ]

    # Assert exactly 1 <resources> tag under vevent properties with multiple <text> children
    res_tags = root.findall(".//x:vevent/x:properties/x:resources", ns)
    assert len(res_tags) == 1
    assert [e.text for e in res_tags[0].findall("x:text", ns)] == [
        "EASEL",
        "PROJECTOR",
        "VCR",
    ]

    # Assert exactly 1 <exdate> tag
    exdate_tags = root.findall(".//x:vevent/x:properties/x:exdate", ns)
    assert len(exdate_tags) == 1
    assert len(exdate_tags[0].findall("x:date-time", ns)) == 2

    # Assert exactly 1 <rdate> tag
    rdate_tags = root.findall(".//x:vevent/x:properties/x:rdate", ns)
    assert len(rdate_tags) == 1
    assert len(rdate_tags[0].findall("x:date-time", ns)) == 2

    # Assert exactly 1 <freebusy> tag under vfreebusy with 2 <period> children
    fb_tags = root.findall(".//x:vfreebusy/x:properties/x:freebusy", ns)
    assert len(fb_tags) == 1
    assert len(fb_tags[0].findall("x:period", ns)) == 2

    # Roundtrip test: from_xcal -> to_xcal -> from_xcal
    cal2 = Calendar.from_xcal(raw_xcal)[0]
    assert cal2.to_xcal() == raw_xcal


def test_categories_multi_value_xml_generation():
    """Test CATEGORIES generates a single property element with multiple text values."""
    event = Event()
    event.add("categories", ["WORK", "MEETING", "DEVELOPMENT"])
    event.add("summary", "Test Multi Categories")
    xml_bytes = event.to_xcal()
    root = ET.fromstring(xml_bytes)
    ns = {"x": "urn:ietf:params:xml:ns:icalendar-2.0"}

    cat_elements = root.findall(".//x:categories", ns)
    assert len(cat_elements) == 1
    texts = [t.text for t in cat_elements[0].findall("x:text", ns)]
    assert texts == ["WORK", "MEETING", "DEVELOPMENT"]


def test_resources_single_and_multi_value_xml_generation():
    """Test RESOURCES generates a single XML element whether single or multi-value."""
    # Single resource
    event1 = Event()
    event1.add("resources", "ROOM-101")
    root1 = ET.fromstring(event1.to_xcal())
    ns = {"x": "urn:ietf:params:xml:ns:icalendar-2.0"}
    res1 = root1.findall(".//x:resources", ns)
    assert len(res1) == 1
    assert [t.text for t in res1[0].findall("x:text", ns)] == ["ROOM-101"]

    # Multiple resources added as separate entries
    event2 = Event()
    event2.add("resources", "PROJECTOR")
    event2.add("resources", "WHITEBOARD")
    event2.add("resources", "SPEAKER")
    root2 = ET.fromstring(event2.to_xcal())
    res2 = root2.findall(".//x:resources", ns)
    assert len(res2) == 1, (
        "Multiple resources must be grouped into a single <resources> tag"
    )
    assert [t.text for t in res2[0].findall("x:text", ns)] == [
        "PROJECTOR",
        "WHITEBOARD",
        "SPEAKER",
    ]


def test_freebusy_multi_value_xml_generation():
    """Test FREEBUSY multi-value grouping under a single <freebusy> element."""
    vfb = FreeBusy()
    start1 = datetime(2026, 10, 26, 9, 0, tzinfo=timezone.utc)
    end1 = datetime(2026, 10, 26, 10, 0, tzinfo=timezone.utc)
    p1 = vPeriod((start1, end1))
    p1.params["FBTYPE"] = "BUSY"

    start2 = datetime(2026, 10, 26, 14, 0, tzinfo=timezone.utc)
    dur2 = timedelta(hours=2)
    p2 = vPeriod((start2, dur2))
    p2.params["FBTYPE"] = "BUSY"

    vfb.add("freebusy", p1)
    vfb.add("freebusy", p2)

    root = ET.fromstring(vfb.to_xcal())
    ns = {"x": "urn:ietf:params:xml:ns:icalendar-2.0"}

    fb_tags = root.findall(".//x:freebusy", ns)
    assert len(fb_tags) == 1, (
        "FREEBUSY periods must be grouped into a single <freebusy> tag"
    )
    periods = fb_tags[0].findall("x:period", ns)
    assert len(periods) == 2


def test_exdate_and_rdate_multi_value_xml_generation():
    """Test EXDATE and RDATE serialize multiple dates in a single element."""
    event = Event()
    dt1 = datetime(2026, 10, 27, 8, 0, tzinfo=timezone.utc)
    dt2 = datetime(2026, 10, 28, 8, 0, tzinfo=timezone.utc)
    event.add("exdate", [dt1, dt2])

    dt3 = datetime(2026, 10, 29, 10, 0, tzinfo=timezone.utc)
    dt4 = datetime(2026, 10, 30, 10, 0, tzinfo=timezone.utc)
    event.add("rdate", [dt3, dt4])

    root = ET.fromstring(event.to_xcal())
    ns = {"x": "urn:ietf:params:xml:ns:icalendar-2.0"}

    ex_tags = root.findall(".//x:exdate", ns)
    assert len(ex_tags) == 1
    assert len(ex_tags[0].findall("x:date-time", ns)) == 2

    r_tags = root.findall(".//x:rdate", ns)
    assert len(r_tags) == 1
    assert len(r_tags[0].findall("x:date-time", ns)) == 2
