# -*- coding: utf-8 -*-
from icalendar.caselessdict import CaselessDict
import unittest

import datetime
import icalendar
import os
import pytz


class TestRecurrence(unittest.TestCase):

    def setUp(self):
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'recurrence.ics'), 'rb') as fp:
            data = fp.read()
        self.cal = icalendar.Calendar.from_ical(data)

    def test_recurrence_exdates_one_line(self):
        first_event = self.cal.walk('vevent')[0]

        self.assertIsInstance(first_event, CaselessDict)
        self.assertEqual(
            first_event['rrule'], {'COUNT': [100], 'FREQ': ['DAILY']}
        )

        self.assertEqual(
            first_event['exdate'].to_ical(),
            b'19960402T010000Z,19960403T010000Z,19960404T010000Z'
        )

        self.assertEqual(
            first_event['exdate'].dts[0].dt,
            pytz.utc.localize(datetime.datetime(1996, 4, 2, 1, 0))
        )

        self.assertEqual(
            first_event['exdate'].dts[1].dt,
            pytz.utc.localize(datetime.datetime(1996, 4, 3, 1, 0))
        )

        self.assertEqual(
            first_event['exdate'].dts[2].dt,
            pytz.utc.localize(datetime.datetime(1996, 4, 4, 1, 0))
        )

    def test_recurrence_exdates_multiple_lines(self):
        event = self.cal.walk('vevent')[1]

        exdate = event['exdate']

        # TODO: DOCUMENT BETTER!
        # In this case we have multiple EXDATE definitions, one per line.
        # Icalendar makes a list out of this instead of zipping it into one
        # vDDDLists object. Actually, this feels correct for me, as it also
        # allows to define different timezones per exdate line - but client
        # code has to handle this as list and not blindly expecting to be able
        # to call event['EXDATE'].to_ical() on it:
        self.assertEqual(isinstance(exdate, list), True)  # multiple EXDATE
        self.assertEqual(exdate[0].to_ical(), b'20120529T100000')

        # TODO: test for embedded timezone information!

    def test_byday_to_ical(self):
        'Test the BYDAY rule is correctly processed by to_ical().'
        TEST_CASES = (
            # Test some YEARLY BYDAY repeats
            ('YEARLY', '1SU', datetime.date(2016,1,3), # 1st Sunday in year
                b'BEGIN:VEVENT\r\nSUMMARY:Event YEARLY 1SU\r\nDTSTART;VALUE=DATE:20160103\r\nRRULE:FREQ=YEARLY;BYDAY=1SU\r\nEND:VEVENT\r\n'),
            ('YEARLY', '53MO', datetime.date(1984,12,31), # 53rd Mon in (leap) year
                b'BEGIN:VEVENT\r\nSUMMARY:Event YEARLY 53MO\r\nDTSTART;VALUE=DATE:19841231\r\nRRULE:FREQ=YEARLY;BYDAY=53MO\r\nEND:VEVENT\r\n'),
            ('YEARLY', '-1TU', datetime.date(1999,12,28), # Last Tues in year
                b'BEGIN:VEVENT\r\nSUMMARY:Event YEARLY -1TU\r\nDTSTART;VALUE=DATE:19991228\r\nRRULE:FREQ=YEARLY;BYDAY=-1TU\r\nEND:VEVENT\r\n'),
            ('YEARLY', '-17WE', datetime.date(2000,9,6), # 17th-last Wed in year
                b'BEGIN:VEVENT\r\nSUMMARY:Event YEARLY -17WE\r\nDTSTART;VALUE=DATE:20000906\r\nRRULE:FREQ=YEARLY;BYDAY=-17WE\r\nEND:VEVENT\r\n'),
            # Test some MONTHLY BYDAY repeats
            ('MONTHLY', '2TH', datetime.date(2003,4,10), # 2nd Thurs in month
                b'BEGIN:VEVENT\r\nSUMMARY:Event MONTHLY 2TH\r\nDTSTART;VALUE=DATE:20030410\r\nRRULE:FREQ=MONTHLY;BYDAY=2TH\r\nEND:VEVENT\r\n'),
            ('MONTHLY', '-3FR', datetime.date(2017,5,12), # 3rd-last Fri in month
                b'BEGIN:VEVENT\r\nSUMMARY:Event MONTHLY -3FR\r\nDTSTART;VALUE=DATE:20170512\r\nRRULE:FREQ=MONTHLY;BYDAY=-3FR\r\nEND:VEVENT\r\n'),
            ('MONTHLY', '-5SA', datetime.date(2053,11,1), # 5th-last Sat in month
                b'BEGIN:VEVENT\r\nSUMMARY:Event MONTHLY -5SA\r\nDTSTART;VALUE=DATE:20531101\r\nRRULE:FREQ=MONTHLY;BYDAY=-5SA\r\nEND:VEVENT\r\n'),
            # Specifically test examples from the report of Issue #518
            # https://github.com/collective/icalendar/issues/518
            ('YEARLY', '9MO', datetime.date(2023,2,27), # 9th Monday in year
                b'BEGIN:VEVENT\r\nSUMMARY:Event YEARLY 9MO\r\nDTSTART;VALUE=DATE:20230227\r\nRRULE:FREQ=YEARLY;BYDAY=9MO\r\nEND:VEVENT\r\n'),
            ('YEARLY', '10MO', datetime.date(2023,3,6), # 10th Monday in year
                b'BEGIN:VEVENT\r\nSUMMARY:Event YEARLY 10MO\r\nDTSTART;VALUE=DATE:20230306\r\nRRULE:FREQ=YEARLY;BYDAY=10MO\r\nEND:VEVENT\r\n'),
            )
        for c in TEST_CASES:
            self._dotest_byday_to_ical(*c)

    def _dotest_byday_to_ical(self, freq, byday, dtstart, expected):
        'Called by test_byday_to_ical() with various parameters'
        event = icalendar.Event()
        event.add('SUMMARY', ' '.join(['Event', freq, byday]))
        event.add('DTSTART', dtstart)
        event.add('RRULE', {'FREQ':[freq], 'BYDAY':byday})
        ical = event.to_ical()
        self.assertEqual(ical, expected)
