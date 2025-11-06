"""
Property parameters are represented as a JSON object where each key-
value pair represents the iCalendar parameter name and its value.
The name of the parameter MUST be in lowercase; the original case of
the parameter value MUST be preserved.
"""

from icalendar import PARTSTAT, ROLE, Event, vCalAddress


def test_vCalAddressExample():
    """Test the example from vCalAddress."""
    addr = vCalAddress.new(
        "jsmith@example.org",
        partstat=PARTSTAT.ACCEPTED,
        rsvp=True,
        role=ROLE.REQ_PARTICIPANT,
    )
    event = Event()
    event.attendees = [addr]
    event.summary = "Meeting"
    jcal = event.to_jcal()
    assert jcal == [
        "vevent",
        [
            [
                "attendee",
                {"partstat": "ACCEPTED", "rsvp": "TRUE", "role": "REQ-PARTICIPANT"},
                "cal-address",
                "mailto:jsmith@example.org",
            ],
            ["summary", {}, "text", "Meeting"],
        ],
        [],
    ]
