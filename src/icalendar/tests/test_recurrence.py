# -*- coding: utf-8 -*-
import icalendar
import pytz
import datetime
import dateutil.parser
import os

from . import unittest


class TestRecurrence(unittest.TestCase):

    def setUp(self):
        directory = os.path.dirname(__file__)
        self.cal = icalendar.Calendar.from_ical(
            open(os.path.join(directory, 'recurrence.ics'), 'rb').read()
        )

    def test_recurrence_exdates_one_line(self):
        first_event = self.cal.walk('vevent')[0]

        self.assertEqual(
            str(first_event['rrule']),
            "CaselessDict({'COUNT': [100], 'FREQ': ['DAILY']})"
        )

        self.assertEqual(
            first_event['exdate'].to_ical(),
            '19960402T010000Z,19960403T010000Z,19960404T010000Z'
        )

        self.assertEqual(
            first_event['exdate'].dts[0].dt,
            datetime.datetime(1996, 4, 2, 1, 0, tzinfo=pytz.utc)
        )

        self.assertEqual(
            first_event['exdate'].dts[1].dt,
            datetime.datetime(1996, 4, 3, 1, 0, tzinfo=pytz.utc)
        )

        self.assertEqual(
            first_event['exdate'].dts[2].dt,
            datetime.datetime(1996, 4, 4, 1, 0, tzinfo=pytz.utc)
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
        self.assertEqual(exdate[0].to_ical(), '20120529T100000')

        # TODO: test for embedded timezone information!
