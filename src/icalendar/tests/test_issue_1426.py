"""Test for GitHub issue #1426:

A property's VALUE parameter (e.g. RDATE;VALUE=PERIOD, TRIGGER;VALUE=DATE-TIME)
was silently dropped on a jCal round-trip. Per :rfc:`7265#section-3.5.1` the
value type is carried by the jCal type identifier and must be turned back into a
VALUE parameter when it is not the property's default value type.

The fixture-based tests here run across every calendar implementation (including
``LazyCalendar``) via the ``calendars`` fixture. Contributed by @lcampanella98.
"""

from icalendar import Component


def _jcal_round_trip(component):
    return Component.from_jcal(component.to_jcal())


def test_non_default_value_param_survives_jcal_round_trip(calendars):
    copy = _jcal_round_trip(calendars.issue_1426)
    event = copy.walk("VEVENT")[0]
    alarm = event.walk("VALARM")[0]

    # PERIOD is not the default for RDATE; DATE-TIME is not the default for
    # TRIGGER (whose default is DURATION) -- so both must be preserved.
    assert event["RDATE"].params["VALUE"] == "PERIOD"
    assert alarm["TRIGGER"].params["VALUE"] == "DATE-TIME"

    # And they survive all the way back to iCalendar.
    ical = copy.to_ical()
    assert b"RDATE;VALUE=PERIOD:" in ical
    assert b"TRIGGER;VALUE=DATE-TIME:" in ical


def test_value_param_kept_or_dropped_per_default_type(calendars):
    """Non-default VALUE is kept, default VALUE is dropped."""
    event = _jcal_round_trip(calendars.issue_1426_value_parameters).walk("VEVENT")[0]

    # DATE is not the default for DTSTART (DATE-TIME) -- kept.
    assert event["DTSTART"].params["VALUE"] == "DATE"
    # URI is the default for CONFERENCE -- dropped.
    assert "VALUE" not in event["CONFERENCE"].params
