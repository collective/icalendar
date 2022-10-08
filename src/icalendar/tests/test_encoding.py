import unittest

import pytest

import datetime
import icalendar
import os
import pytz

@pytest.mark.parametrize('field, expected_value', [
    ('PRODID', '-//Plönë.org//NONSGML plone.app.event//EN'),
    ('X-WR-CALDESC', 'test non ascii: äöü ÄÖÜ €'),
])
def test_calendar_from_ical_respects_unicode(field, expected_value, calendars):
    cal = calendars.calendar_with_unicode
    assert cal[field].to_ical().decode('utf-8') == expected_value

@pytest.mark.parametrize('test_input, field, expected_value', [
    ('event_with_unicode_fields', 'SUMMARY', 'Non-ASCII Test: ÄÖÜ äöü €'),
    ('event_with_unicode_fields', 'DESCRIPTION', 'icalendar should be able to handle non-ascii: €äüöÄÜÖ.'),
    ('event_with_unicode_fields', 'LOCATION', 'Tribstrül'),
    # Non-unicode characters in summary
    # https://github.com/collective/icalendar/issues/64
    ('issue_64_event_with_non_ascii_summary', 'SUMMARY', 'åäö'),
    # Unicode characters in summary
    ('issue_64_event_with_ascii_summary', 'SUMMARY', 'abcdef'),
])
def test_event_from_ical_respects_unicode(test_input, field, expected_value, events):
    event = events[test_input]
    assert event[field].to_ical().decode('utf-8') == expected_value

def test_events_parameter_unicoded(events):
    '''chokes on umlauts in ORGANIZER
    https://github.com/collective/icalendar/issues/101
    '''
    assert events.issue_101_icalendar_chokes_on_umlauts_in_organizer['ORGANIZER'].params['CN'] == 'acme, ädmin'


class TestEncoding(unittest.TestCase):
    def test_create_to_ical(self):
        cal = icalendar.Calendar()

        cal.add('prodid', "-//Plönë.org//NONSGML plone.app.event//EN")
        cal.add('version', "2.0")
        cal.add('x-wr-calname', "äöü ÄÖÜ €")
        cal.add('x-wr-caldesc', "test non ascii: äöü ÄÖÜ €")
        cal.add('x-wr-relcalid', "12345")

        event = icalendar.Event()
        event.add(
            'dtstart',
            pytz.utc.localize(datetime.datetime(2010, 10, 10, 10, 0, 0))
        )
        event.add(
            'dtend',
            pytz.utc.localize(datetime.datetime(2010, 10, 10, 12, 0, 0))
        )
        event.add(
            'created',
            pytz.utc.localize(datetime.datetime(2010, 10, 10, 0, 0, 0))
        )
        event.add('uid', '123456')
        event.add('summary', 'Non-ASCII Test: ÄÖÜ äöü €')
        event.add(
            'description',
            'icalendar should be able to de/serialize non-ascii.'
        )
        event.add('location', 'Tribstrül')
        cal.add_component(event)

        ical_lines = cal.to_ical().splitlines()
        cmp = b'PRODID:-//Pl\xc3\xb6n\xc3\xab.org//NONSGML plone.app.event//EN'
        self.assertTrue(cmp in ical_lines)

    def test_create_event_simple(self):
        event = icalendar.Event()
        event.add(
            "dtstart",
            pytz.utc.localize(datetime.datetime(2010, 10, 10, 0, 0, 0))
        )
        event.add("summary", "åäö")
        out = event.to_ical()
        summary = b'SUMMARY:\xc3\xa5\xc3\xa4\xc3\xb6'
        self.assertTrue(summary in out.splitlines())

    def test_unicode_parameter_name(self):
        # Test for issue #80
        cal = icalendar.Calendar()
        event = icalendar.Event()
        event.add('DESCRIPTION', 'äöüßÄÖÜ')
        cal.add_component(event)
        c = cal.to_ical()
        self.assertEqual(
            c,
            b'BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDESCRIPTION:'
            + b'\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f\xc3\x84\xc3\x96\xc3\x9c\r\n'
            + b'END:VEVENT\r\nEND:VCALENDAR\r\n'
        )

