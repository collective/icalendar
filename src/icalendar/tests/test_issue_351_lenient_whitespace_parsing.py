"""Regression tests for issue 351."""


def test_parse_calendar_with_whitespace_around_delimiters(calendars):
    cal = calendars["issue_351_whitespace_in_property_and_params"]

    refresh_interval = cal["REFRESH-INTERVAL"]
    assert refresh_interval.to_ical() == b"P2D"
    assert refresh_interval.params["VALUE"] == "DURATION"
