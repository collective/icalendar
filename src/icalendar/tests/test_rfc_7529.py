"""This tests the compatibility with RFC 7529.

See
- https://github.com/collective/icalendar/issues/653
- https://www.rfc-editor.org/rfc/rfc7529.html
"""
import pytest


@pytest.mark.parametrize(
    "uid,scale",
    [
        ("4.3.1", "CHINESE"),
        ("4.3.2", "ETHIOPIC"),
        ("4.3.3", "HEBREW"),
        ("4.3.4", "GREGORIAN"),
    ]
)
def test_rscale(calendars, uid, scale):
    """Check that the RSCALE is parsed correctly."""
    event = calendars.rfc_7529.walk(select=lambda c: c.get("UID") == uid)[0]
    print(event.errors)
    rrule = event["RRULE"]
    print(rrule)
    assert rrule["RSCALE"] == [scale]
