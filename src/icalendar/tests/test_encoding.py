import unittest

import pytest

import datetime
import icalendar
import os
import pytz


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

