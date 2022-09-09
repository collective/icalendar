import unittest

import pytest

import datetime
import icalendar
import os
import pytz
from dateutil import tz

try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo


class TestEncoding(unittest.TestCase):

    def test_create_from_ical(self):
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'encoding.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)

        self.assertEqual(cal['prodid'].to_ical().decode('utf-8'),
                         "-//Plönë.org//NONSGML plone.app.event//EN")
        self.assertEqual(cal['X-WR-CALDESC'].to_ical().decode('utf-8'),
                         "test non ascii: äöü ÄÖÜ €")

        event = cal.walk('VEVENT')[0]
        self.assertEqual(event['SUMMARY'].to_ical().decode('utf-8'),
                         'Non-ASCII Test: ÄÖÜ äöü €')
        self.assertEqual(
            event['DESCRIPTION'].to_ical().decode('utf-8'),
            'icalendar should be able to handle non-ascii: €äüöÄÜÖ.'
        )
        self.assertEqual(event['LOCATION'].to_ical().decode('utf-8'),
                         'Tribstrül')

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

@pytest.mark.parametrize('event_name', [
    # Non-unicode characters in summary
    'issue_64_event_with_non_unicode_summary',
    # Unicode characters in summary
    'issue_64_event_with_unicode_summary',
    # chokes on umlauts in ORGANIZER
    'issue_101_icalendar_chokes_on_umlauts_in_organizer'
])
def test_events_unicoded(events, event_name):
    '''Issue #64 - Event.to_ical() fails for unicode strings
       Issue #101 - icalendar is choking on umlauts in ORGANIZER

    https://github.com/collective/icalendar/issues/64
    https://github.com/collective/icalendar/issues/101
    '''
    event = getattr(events, event_name)
    assert event.to_ical() == event.raw_ics

def test_parses_event_with_non_ascii_tzid_issue_237(events, timezone):
    """Issue #237 - Fail to parse timezone with non-ascii TZID
    see https://github.com/collective/icalendar/issues/237
    """
    start = events.issue_237_fail_to_parse_timezone_with_non_ascii_tzid.decoded('DTSTART')
    expected = datetime.datetime(2017, 5, 11, 13, 30, tzinfo=timezone('America/Sao_Paulo'))
    assert start == expected

def test_parses_timezone_with_non_ascii_tzid_issue_237(timezones):
    """Issue #237 - Fail to parse timezone with non-ascii TZID
    see https://github.com/collective/icalendar/issues/237
    """
    assert timezones.issue_237_brazilia_standard['tzid'] == '(UTC-03:00) Brasília'

@pytest.mark.parametrize('timezone_name', ['standard', 'daylight'])
def test_parses_timezone_with_non_ascii_tzname_issue_273(timezones, timezone_name):
    """Issue #237 - Fail to parse timezone with non-ascii TZID
    see https://github.com/collective/icalendar/issues/237
    """
    assert timezones.issue_237_brazilia_standard.walk(timezone_name)[0]['TZNAME'] == f'Brasília {timezone_name}'

