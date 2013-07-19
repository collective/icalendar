# -*- coding: utf-8 -*-
import icalendar
import pytz
import datetime
import dateutil.parser
import os

from . import unittest


class TestRecurrence(unittest.TestCase):

    def test_recurrence_create_from_ical(self):
        directory = os.path.dirname(__file__)
        cal = icalendar.Calendar.from_ical(
                open(os.path.join(directory, 'recurrence.ics'), 'rb').read()
        )

        first_event = cal.walk('vevent')[0]

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
