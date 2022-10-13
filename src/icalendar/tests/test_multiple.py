"""An example with multiple VCALENDAR components"""
from icalendar import Calendar
from icalendar.prop import vText



def test_multiple(calendars):
    """Check opening multiple calendars."""

    cals = calendars.multiple.multiple_calendar_components

    assert len(cals) == 2
    assert [comp.name for comp in cals[0].walk()] == ['VCALENDAR', 'VEVENT']
    assert [comp.name for comp in cals[1].walk()] == ['VCALENDAR', 'VEVENT', 'VEVENT']
    assert cals[0]['prodid'] == vText('-//Mozilla.org/NONSGML Mozilla Calendar V1.0//EN')
