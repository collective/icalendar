# -*- coding: utf-8 -*-
from icalendar.caselessdict import CaselessDict
from icalendar.tests import unittest

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
