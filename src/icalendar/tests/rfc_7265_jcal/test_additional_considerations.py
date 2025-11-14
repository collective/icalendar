"""These are tests for considerations that are specific to our implementation."""

from icalendar import Event
from icalendar.prop import vText


def test_adding_a_description_several_times_works():
    """We should be able to add valid parameters several times."""
    event = Event()
    en = vText("English description", params={"language": "en"})
    de = vText("Deutsche Beschreibung", params={"language": "de"})
    event.add("DESCRIPTION", en)
    event.add("DESCRIPTION", de)
    jcal = event.to_jcal()
    assert jcal[1][0] == [
        "description",
        {"language": "en"},
        "text",
        "English description",
    ]
    assert jcal[1][1] == [
        "description",
        {"language": "de"},
        "text",
        "Deutsche Beschreibung",
    ]
