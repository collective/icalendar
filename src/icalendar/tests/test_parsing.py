"""Tests checking that parsing works"""

import base64
from datetime import datetime

import pytest

from icalendar import vBinary, vRecur
from icalendar.cal.calendar import Calendar
from icalendar.cal.component_factory import ComponentFactory
from icalendar.cal.event import Event
from icalendar.parser import (
    Contentline,
    Parameters,
    _escape_char,
    _foldline,
    _unescape_char,
)


@pytest.mark.parametrize(
    ("raw_content_line", "expected_output"),
    [
        # Issue #142 - Multivalued parameters. This is needed for VCard 3.0.
        # see https://github.com/collective/icalendar/pull/142
        (
            "TEL;TYPE=HOME,VOICE:000000000",
            ("TEL", Parameters({"TYPE": ["HOME", "VOICE"]}), "000000000"),
        ),
        # Issue #143 - Allow dots in property names. Another vCard related issue.
        # see https://github.com/collective/icalendar/pull/143
        (
            "ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR:;;This is the Adress 08; Some City;;12345;Germany",
            (
                "ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR",
                Parameters(),
                ";;This is the Adress 08; Some City;;12345;Germany",
            ),
        ),
        (
            "ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.X-ABLABEL:",
            (
                "ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.X-ABLABEL",
                Parameters(),
                "",
            ),
        ),
    ],
)
def test_content_lines_parsed_properly(raw_content_line, expected_output):
    assert Contentline.from_ical(raw_content_line).parts() == expected_output


@pytest.mark.parametrize(
    ("raw_content_line", "expected_altrep"),
    [
        # Literal percent escapes in a parameter value (common in URIs) must
        # survive parsing. They collided with the parser's internal
        # ``\\,`` -> ``%2C`` transport encoding and were silently decoded.
        ('X-P;ALTREP="http://x/a%2Cb%3Ac%3Bd%5Ce":v', "http://x/a%2Cb%3Ac%3Bd%5Ce"),
        ('X-P;ALTREP="http://x/%2520":v', "http://x/%2520"),
        # Same value unquoted, with a backslash-escaped colon protecting the
        # URI scheme separator. Percent escapes must survive here too.
        ("X-P;ALTREP=http\\://x/a%2Cb%3Ac%3Bd%5Ce:v", "http://x/a%2Cb%3Ac%3Bd%5Ce"),
        # A backslash-escaped delimiter still decodes to the bare character.
        ("X-P;ALTREP=a\\,b:v", "a,b"),
    ],
)
def test_percent_escapes_in_parameter_values_are_preserved(
    raw_content_line, expected_altrep
):
    assert Contentline(raw_content_line).parts()[1]["ALTREP"] == expected_altrep


@pytest.mark.parametrize(
    "timezone_info",
    [
        # General timezone aware dates in ical string
        (b"DTSTART;TZID=America/New_York:20130907T120000"),
        (b"DTEND;TZID=America/New_York:20130907T170000"),
        # Specific timezone aware exdates in ical string
        (b"EXDATE;TZID=America/New_York:20131012T120000"),
        (b"EXDATE;TZID=America/New_York:20131011T120000"),
    ],
)
def test_timezone_info_present_in_ical_issue_112(events, timezone_info):
    """Issue #112 - No timezone info on EXDATE

    https://github.com/collective/icalendar/issues/112
    """
    assert timezone_info in events.issue_112_missing_tzinfo_on_exdate.to_ical()


def test_timezone_name_parsed_issue_112(events):
    """Issue #112 - No timezone info on EXDATE

    https://github.com/collective/icalendar/issues/112
    """
    assert (
        events.issue_112_missing_tzinfo_on_exdate["exdate"][0].dts[0].dt.tzname()
        == "EDT"
    )


def test_issue_157_removes_trailing_semicolon(events):
    """Issue #157 - Recurring rules and trailing semicolons

    https://github.com/collective/icalendar/pull/157
    """
    recur = events.issue_157_removes_trailing_semicolon.decoded("RRULE")
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b"FREQ=YEARLY;BYDAY=1SU;BYMONTH=11"


@pytest.mark.parametrize(
    "event_name",
    [
        # https://github.com/collective/icalendar/pull/100
        ("issue_100_transformed_doctests_into_unittests"),
        ("issue_184_broken_representation_of_period"),
        # PERIOD should be put back into shape
        "issue_156_RDATE_with_PERIOD",
        "issue_156_RDATE_with_PERIOD_list",
        "event_with_unicode_organizer",
    ],
)
def test_event_to_ical_is_inverse_of_from_ical(events, event_name):
    """Make sure that an event's ICS is equal to the ICS it was made from."""
    event = events[event_name]
    assert event.to_ical().splitlines() == event.raw_ics.splitlines()
    assert event.to_ical() == event.raw_ics


def test_decode_rrule_attribute_error_issue_70(events):
    # Issue #70 - e.decode("RRULE") causes Attribute Error
    # see https://github.com/collective/icalendar/issues/70
    recur = events.issue_70_rrule_causes_attribute_error.decoded("RRULE")
    assert isinstance(recur, vRecur)
    assert recur.to_ical() == b"FREQ=WEEKLY;UNTIL=20070619T225959;INTERVAL=1"


def test_description_parsed_properly_issue_53(events):
    """Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    """
    assert (
        b"July 12 at 6:30 PM"
        in events.issue_53_description_parsed_properly["DESCRIPTION"].to_ical()
    )


@pytest.mark.parametrize(
    "escape_sequence",
    [
        r"\n",
        r"\N",
        r"\,",
        r"\;",
        r"\\",
        "^n",
        "^^",
        "^'",
    ],
)
@pytest.mark.parametrize("line_limit", range(60, 91))
def test_foldline_does_not_split_escape_sequences_issue_1501(
    escape_sequence, line_limit
):
    """Issue #1501 - line folding must not split escape sequences."""
    prefix = "DESCRIPTION:" + ("a" * (line_limit - len("DESCRIPTION:") - 2))
    line = prefix + escape_sequence + "after fold"

    folded = _foldline(line, limit=line_limit)

    assert "\r\n " in folded
    assert (escape_sequence[0] + "\r\n " + escape_sequence[1]) not in folded


@pytest.mark.parametrize("escape_sequence", [r"\n", "^n"])
def test_foldline_does_not_split_escape_sequences_across_multiple_lines_issue_1501(
    escape_sequence,
):
    """Issue #1501 - escape-aware folding applies after the first fold too."""
    line_limit = 60
    prefix = "DESCRIPTION:" + ("a" * (line_limit - len("DESCRIPTION:") - 2))
    repeated_segment = escape_sequence + ("b" * (line_limit - len(escape_sequence) - 1))
    line = prefix + repeated_segment + escape_sequence + "after fold"

    folded = _foldline(line, limit=line_limit)

    assert folded.count("\r\n ") >= 2
    assert (escape_sequence[0] + "\r\n " + escape_sequence[1]) not in folded


def test_raises_value_error_for_properties_without_parent_pull_179():
    """Found an issue where from_ical() would raise IndexError for
    properties without parent components.

    https://github.com/collective/icalendar/pull/179
    """
    with pytest.raises(ValueError):
        Calendar.from_ical("VERSION:2.0")


def test_tzid_parsed_properly_issue_53(timezones):
    """Issue #53 - Parsing failure on some descriptions?

    https://github.com/collective/icalendar/issues/53
    """
    assert (
        timezones.issue_53_tzid_parsed_properly["tzid"].to_ical() == b"America/New_York"
    )


def test_timezones_to_ical_is_inverse_of_from_ical(timezones):
    """Issue #55 - Parse error on utc-offset with seconds value
    see https://github.com/collective/icalendar/issues/55"""
    timezone = timezones["issue_55_parse_error_on_utc_offset_with_seconds"]
    assert timezone.to_ical() == timezone.raw_ics


@pytest.mark.parametrize(
    ("date", "expected_output"),
    [
        (datetime(2012, 7, 16, 0, 0, 0), b"DTSTART:20120716T000000Z"),
        (datetime(2021, 11, 17, 15, 9, 15), b"DTSTART:20211117T150915Z"),
    ],
)
def test_no_tzid_when_utc(utc, date, expected_output):
    """Issue #58  - TZID on UTC DATE-TIMEs
       Issue #335 - UTC timezone identification is broken

    https://github.com/collective/icalendar/issues/58
    https://github.com/collective/icalendar/issues/335
    """
    # According to RFC 5545: "The TZID property parameter MUST NOT be
    # applied to DATE-TIME or TIME properties whose time values are
    # specified in UTC.
    date = date.replace(tzinfo=utc)
    event = Event()
    event.add("dtstart", date)
    assert expected_output in event.to_ical()


def test_vBinary_base64_encoded_issue_82():
    """Issue #82 - vBinary __repr__ called rather than to_ical from
                   container types
    https://github.com/collective/icalendar/issues/82
    """
    b = vBinary("text")
    b.params["FMTTYPE"] = "text/plain"
    assert b.to_ical() == base64.b64encode(b"text")


def test_creates_event_with_base64_encoded_attachment_issue_82(events):
    """Issue #82 - vBinary __repr__ called rather than to_ical from
                   container types
    https://github.com/collective/icalendar/issues/82
    """
    b = vBinary("text")
    b.params["FMTTYPE"] = "text/plain"
    event = Event()
    event.add("ATTACH", b)
    assert event.to_ical() == events.issue_82_expected_output.raw_ics


@pytest.mark.parametrize(
    "calendar_name",
    [
        # Issue #466 - [BUG] TZID timezone is ignored when forward-slash is used
        # https://github.com/collective/icalendar/issues/466
        "issue_466_respect_unique_timezone",
        "issue_466_convert_tzid_with_slash",
    ],
)
def test_handles_unique_tzid(calendars, in_timezone, calendar_name):
    calendar = calendars[calendar_name]
    event = calendar.walk("VEVENT")[0]
    print(vars(event))
    start_dt = event["dtstart"].dt
    end_dt = event["dtend"].dt
    assert start_dt == in_timezone(datetime(2022, 10, 21, 20, 0, 0), "Europe/Stockholm")
    assert end_dt == in_timezone(datetime(2022, 10, 21, 21, 0, 0), "Europe/Stockholm")


@pytest.mark.parametrize(
    ("event_name", "expected_cn", "expected_ics"),
    [
        (
            "event_with_escaped_characters",
            r"that, that; %th%%at%\ that:",
            "это, то; that\\ %th%%at%:",
        ),
        ("event_with_escaped_character1", r"Society, 2014", "that"),
        ("event_with_escaped_character2", r"Society\ 2014", "that"),
        ("event_with_escaped_character3", r"Society; 2014", "that"),
        ("event_with_escaped_character4", r"Society: 2014", "that"),
    ],
)
def test_escaped_characters_read(event_name, expected_cn, expected_ics, events):
    event = events[event_name]
    assert event["ORGANIZER"].params["CN"] == expected_cn
    assert event["ORGANIZER"].to_ical() == expected_ics.encode("utf-8")


def test_unescape_char():
    assert _unescape_char(b"123") == b"123"
    assert _unescape_char(b"\\n") == b"\n"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a\rb", r"a\nb"),
        ("a\r\nb", r"a\nb"),
        ("a\nb", r"a\nb"),
        ("a\rb\r\nc\nd", r"a\nb\nc\nd"),
        ("\ra\n", r"\na\n"),
    ],
)
def test_escape_char_transforms_lone_carriage_return(value, expected):
    r"""A lone ``\r`` must be transformed, not left raw in the content line."""
    assert _escape_char(value) == expected


def test_lone_carriage_return_cannot_inject_content_line():
    event = Event()
    event.add("SUMMARY", "safe\rINJECTED:evil")
    assert b"\rINJECTED" not in event.to_ical()
    assert event.to_ical() == (
        b"BEGIN:VEVENT\r\nSUMMARY:safe\\nINJECTED:evil\r\nEND:VEVENT\r\n"
    )


def test_split_on_unescaped_comma():
    """Test splitting on unescaped commas."""
    from icalendar.parser import split_on_unescaped_comma

    # Simple case
    assert split_on_unescaped_comma("a,b,c") == ["a", "b", "c"]

    # Escaped comma
    assert split_on_unescaped_comma("a\\,b,c") == ["a,b", "c"]

    # Multiple escaped commas
    assert split_on_unescaped_comma("a\\,b\\,c") == ["a,b,c"]

    # Mixed
    assert split_on_unescaped_comma("Work,Personal\\, Urgent") == [
        "Work",
        "Personal, Urgent",
    ]

    # Empty string
    assert split_on_unescaped_comma("") == [""]

    # Only commas
    assert split_on_unescaped_comma(",,,") == ["", "", "", ""]

    # Trailing comma
    assert split_on_unescaped_comma("a,b,") == ["a", "b", ""]

    # Leading comma
    assert split_on_unescaped_comma(",a,b") == ["", "a", "b"]

    # Other escaped chars
    assert split_on_unescaped_comma("a\\;b,c\\nd") == ["a;b", "c\nd"]


def test_create_a_component():
    """Create a component with the factory."""
    factory = ComponentFactory()
    my_component_class = factory.get_component_class("My-Component")
    assert my_component_class.name == "MY-COMPONENT"
    assert my_component_class.__name__ == "MyComponent"
