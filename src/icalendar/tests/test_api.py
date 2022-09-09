'''Tests checking that *the* way of doing things works'''

from icalendar import Event


def test_adding_x_apple_structured_location_issue_116_117(events):
    '''Issue #116/#117 - How to add 'X-APPLE-STRUCTURED-LOCATION'

    https://github.com/collective/icalendar/issues/116
    https://github.com/collective/icalendar/issues/117
    '''
    event = Event()
    event.add(
        'X-APPLE-STRUCTURED-LOCATION',
        'geo:-33.868900,151.207000',
        parameters={
            'VALUE': 'URI',
            'X-ADDRESS': '367 George Street Sydney CBD NSW 2000',
            'X-APPLE-RADIUS': '72',
            'X-TITLE': '367 George Street'
        }
    )

    assert event.to_ical() == events.issue_116_117_add_x_apple_structured.raw_ics

