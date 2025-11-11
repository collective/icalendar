"""
Property parameters are represented as a JSON object where each key-
value pair represents the iCalendar parameter name and its value.
The name of the parameter MUST be in lowercase; the original case of
the parameter value MUST be preserved.
"""

from icalendar import PARTSTAT, ROLE, VPROPERTY, Event, vCalAddress
from icalendar.parser import Parameters


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


def test_parameter_conversion_is_handed_over_to_parameter(v_prop: VPROPERTY, mock):
    """The parameters are part of the jcal conversion."""
    example = v_prop.examples()[0]
    assert isinstance(example.params, Parameters)
    example.params = mock
    return_value = example.params.to_jcal.return_value
    assert (
        return_value == example.params.to_jcal.return_value == example.params.to_jcal()
    )
    jcal = example.to_jcal("X-NAME")
    mock.to_jcal.assert_called_once()
    assert len(jcal) >= 4
    assert jcal[1] == return_value
    assert jcal[0] == "X-NAME"
    assert jcal[2] == example.params.value
