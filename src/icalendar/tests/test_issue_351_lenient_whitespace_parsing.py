"""Regression tests for issue 351."""

from icalendar.parser.content_line import _strip_ows_around_delimiters


def test_parse_calendar_with_whitespace_around_delimiters(calendars):
    cal = calendars["issue_351_whitespace_in_property_and_params"]

    refresh_interval = cal["REFRESH-INTERVAL"]
    assert refresh_interval.to_ical() == b"P2D"
    assert refresh_interval.params["VALUE"] == "DURATION"


def test_strip_ows_around_delimiters_simple_regex_path():
    assert (
        _strip_ows_around_delimiters('VALUE = DURATION ; X-FOO = BAR')
        == 'VALUE=DURATION;X-FOO=BAR'
    )


def test_strip_ows_around_delimiters_preserves_quoted_text():
    assert (
        _strip_ows_around_delimiters('ALTREP="cid:part1 ; keep = this" ; VALUE = TEXT')
        == 'ALTREP="cid:part1 ; keep = this";VALUE=TEXT'
    )
