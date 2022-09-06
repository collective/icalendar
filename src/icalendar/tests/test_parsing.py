import base64

from icalendar import Event, vBinary

def test_vBinary_base64_encoded_issue_82():
    '''Issue #82 - vBinary __repr__ called rather than to_ical from
                   container types
    https://github.com/collective/icalendar/issues/82
    '''
    b = vBinary('text')
    b.params['FMTTYPE'] = 'text/plain'
    assert b.to_ical() == base64.b64encode(b'text')

def test_creates_event_with_base64_encoded_attachment_issue_82(events):
    '''Issue #82 - vBinary __repr__ called rather than to_ical from
                   container types
    https://github.com/collective/icalendar/issues/82
    '''
    b = vBinary('text')
    b.params['FMTTYPE'] = 'text/plain'
    event = Event()
    event.add('ATTACH', b)
    assert event.to_ical() == events.issue_82_expected_output.raw_ics
