import pytest

from icalendar import Component, Event


def test_ignore_exceptions_on_broken_events_issue_104(events):
    """Issue #104 - line parsing error in a VEVENT
    (which has ignore_exceptions). Should mark the event broken
    but not raise an exception.

    https://github.com/collective/icalendar/issues/104
    """
    assert events.issue_104_mark_events_broken.errors == [
        (None, "Content line could not be parsed into parts: 'X': Invalid content line")
    ]


def test_ignore_exceptions_on_broken_calendars_issue_104(calendars):
    """Issue #104 - changed to record errors instead of raising for issue #399.

    https://github.com/collective/icalendar/issues/399
    """
    calendar = calendars.issue_104_broken_calendar
    assert calendar.errors == [
        (None, "Content line could not be parsed into parts: 'X': Invalid content line")
    ]


def test_issue_399_malformed_lines_are_handled_consistently(calendars):
    """Malformed content lines are skipped and recorded for every component."""
    bare_x_calendar = calendars.issue_104_broken_calendar
    malformed_x_property_calendar = calendars.issue_399_malformed_x_property

    assert bare_x_calendar.errors == [
        (None, "Content line could not be parsed into parts: 'X': Invalid content line")
    ]
    assert malformed_x_property_calendar.walk("VEVENT")[0].errors == [
        (
            None,
            (
                "Content line could not be parsed into parts: "
                "'X-APPLE-RADIUS=49.91307046514149': "
                "X-APPLE-RADIUS=49.91307046514149"
            ),
        )
    ]
    assert b"\r\nX\r\n" not in bare_x_calendar.to_ical()
    assert b"X-APPLE-RADIUS" not in malformed_x_property_calendar.to_ical()


def test_strict_parsing_can_be_enabled_globally(calendars, monkeypatch):
    """The global strict setting still raises for malformed content lines."""
    monkeypatch.setattr(Component, "ignore_exceptions", False)

    with pytest.raises(
        ValueError,
        match=r"^Content line could not be parsed into parts: 'X': Invalid content line$",
    ):
        calendars.issue_104_broken_calendar.subcomponents


def test_event_override_preserves_tolerant_parsing(calendars, monkeypatch):
    """Events remain tolerant unless their explicit override is changed."""
    monkeypatch.setattr(Component, "ignore_exceptions", False)

    parsed = calendars.issue_399_malformed_x_property
    assert parsed.walk("VEVENT")[0].errors == [
        (
            None,
            (
                "Content line could not be parsed into parts: "
                "'X-APPLE-RADIUS=49.91307046514149': "
                "X-APPLE-RADIUS=49.91307046514149"
            ),
        )
    ]
    assert b"X-APPLE-RADIUS" not in parsed.to_ical()

    monkeypatch.setattr(Event, "ignore_exceptions", False)
    with pytest.raises(
        ValueError,
        match=r"^Content line could not be parsed into parts: 'X-APPLE-RADIUS=49\.91307046514149': X-APPLE-RADIUS=49\.91307046514149$",
    ):
        calendars.issue_399_malformed_x_property.subcomponents


def test_rdate_dosent_become_none_on_invalid_input_issue_464(events):
    """Issue #464 - [BUG] RDATE can become None if value is invalid
    https://github.com/collective/icalendar/issues/464
    """
    event = events.issue_464_invalid_rdate

    # After VALUE parameter fix, the assertion checks for the full value string
    # in the error message, making the test more flexible
    assert len(event.errors) == 1
    assert event.errors[0][0] == "RDATE"
    assert "Expected period format" in event.errors[0][1]
    assert "199709T180000Z/PT5H30M" in event.errors[0][1]
    assert b"RDATE:None" not in event.to_ical()


@pytest.mark.parametrize(
    "calendar_name",
    [
        "big_bad_calendar",
        "small_bad_calendar",
        "multiple_calendar_components",
        "pr_480_summary_with_colon",
    ],
)
def test_error_message_doesnt_get_too_big(calendars, calendar_name):
    with pytest.raises(ValueError) as exception:
        calendars[calendar_name]
    # Ignore part before first : for the test.
    assert len(str(exception).split(": ", 1)[1]) <= 100
