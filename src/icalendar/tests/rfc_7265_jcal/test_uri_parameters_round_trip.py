"""Property parameters on URI-typed properties must survive a jCal round-trip.

``vUri.from_jcal`` used to pass the parsed parameters as the second *positional*
argument. Unlike every other value type, ``vUri.__new__`` takes an ``encoding``
argument in that slot (``vUri(value, encoding, /, params=None)``), so the
:class:`~icalendar.parser.Parameters` object was bound to ``encoding`` and
silently discarded, leaving ``params`` at its default of ``None``.

As a result parameters such as ``FMTTYPE`` (ATTACH), ``FEATURE``/``LABEL``
(CONFERENCE) or ``RELTYPE`` (RELATED-TO) were dropped whenever a URI property was
read back from jCal, breaking the round-trip required by :rfc:`7265`.
"""

from icalendar import Calendar, Component, Event, vUri
from icalendar.parser import Parameters


def _jcal_round_trip(component: Component) -> Component:
    return Component.from_jcal(component.to_jcal())


def test_vuri_from_jcal_keeps_parameters():
    """The root cause: ``vUri.from_jcal`` must attach the parsed parameters."""
    jcal_property = ["attach", {"fmttype": "text/plain"}, "uri", "http://example.com"]
    uri = vUri.from_jcal(jcal_property)
    assert uri.params == Parameters({"FMTTYPE": "text/plain"})
    # The value (and the ``encoding`` slot the parameters used to be bound to)
    # is still parsed correctly.
    assert str(uri) == "http://example.com"


def test_attach_fmttype_survives_jcal_round_trip():
    event = Event()
    event.add("UID", "1")
    event.add(
        "ATTACH",
        vUri("http://example.com/report.txt", params={"FMTTYPE": "text/plain"}),
    )
    restored = _jcal_round_trip(event)
    assert restored["ATTACH"].params["FMTTYPE"] == "text/plain"
    assert b"ATTACH;FMTTYPE=text/plain:" in restored.to_ical()


def test_conference_multiple_parameters_survive_jcal_round_trip():
    """Several parameters on the same URI property are all preserved."""
    event = Event()
    event.add("UID", "1")
    event.add(
        "CONFERENCE",
        vUri("tel:+1-555-0100", params={"FEATURE": "AUDIO", "LABEL": "Call in"}),
    )
    restored = _jcal_round_trip(event)
    params = restored["CONFERENCE"].params
    assert params["FEATURE"] == "AUDIO"
    assert params["LABEL"] == "Call in"


def test_jcal_round_trip_is_idempotent_for_uri_parameters():
    """``to_jcal`` of the reparsed component equals the original jCal."""
    calendar = Calendar()
    calendar.add("VERSION", "2.0")
    calendar.add("PRODID", "-//test//EN")
    event = Event()
    event.add("UID", "1")
    event.add(
        "ATTACH", vUri("http://example.com/x.txt", params={"FMTTYPE": "text/plain"})
    )
    event.add(
        "CONFERENCE", vUri("https://chat.example.com/", params={"FEATURE": "VIDEO"})
    )
    calendar.add_component(event)

    jcal = calendar.to_jcal()
    assert Component.from_jcal(jcal).to_jcal() == jcal
