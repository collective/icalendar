"""Check that we convert the examples propertly."""

from icalendar.parser_tools import to_unicode


def test_convert_coffee(calendars):
    """convert the unknown value propertly"""
    calendar = calendars.rfc_7265_unknown_parameter
    ical = calendar.to_ical().decode()
    print(to_unicode(ical))
    assert r"X-COFFEE-DATA:Stenophylla;Guinea\\\,Africa" in ical
