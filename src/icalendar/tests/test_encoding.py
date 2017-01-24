# -*- coding: utf-8 -*-
from icalendar.tests import unittest

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
                         u"-//Plönë.org//NONSGML plone.app.event//EN")
        self.assertEqual(cal['X-WR-CALDESC'].to_ical().decode('utf-8'),
                         u"test non ascii: äöü ÄÖÜ €")

        event = cal.walk('VEVENT')[0]
        self.assertEqual(event['SUMMARY'].to_ical().decode('utf-8'),
                         u'Non-ASCII Test: ÄÖÜ äöü €')
        self.assertEqual(
            event['DESCRIPTION'].to_ical().decode('utf-8'),
            u'icalendar should be able to handle non-ascii: €äüöÄÜÖ.'
        )
        self.assertEqual(event['LOCATION'].to_ical().decode('utf-8'),
                         u'Tribstrül')

    def test_create_to_ical(self):
        cal = icalendar.Calendar()

        cal.add('prodid', u"-//Plönë.org//NONSGML plone.app.event//EN")
        cal.add('version', u"2.0")
        cal.add('x-wr-calname', u"äöü ÄÖÜ €")
        cal.add('x-wr-caldesc', u"test non ascii: äöü ÄÖÜ €")
        cal.add('x-wr-relcalid', u"12345")

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
        event.add('uid', u'123456')
        event.add('summary', u'Non-ASCII Test: ÄÖÜ äöü €')
        event.add(
            'description',
            u'icalendar should be able to de/serialize non-ascii.'
        )
        event.add('location', u'Tribstrül')
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
        event.add("summary", u"åäö")
        out = event.to_ical()
        summary = b'SUMMARY:\xc3\xa5\xc3\xa4\xc3\xb6'
        self.assertTrue(summary in out.splitlines())

    def test_unicode_parameter_name(self):
        # Test for issue #80
        cal = icalendar.Calendar()
        event = icalendar.Event()
        event.add(u'DESCRIPTION', u'äöüßÄÖÜ')
        cal.add_component(event)
        c = cal.to_ical()
        self.assertEqual(
            c,
            b'BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDESCRIPTION:'
            + b'\xc3\xa4\xc3\xb6\xc3\xbc\xc3\x9f\xc3\x84\xc3\x96\xc3\x9c\r\n'
            + b'END:VEVENT\r\nEND:VCALENDAR\r\n'
        )
