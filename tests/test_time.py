# -*- coding: utf-8 -*-
import unittest

import datetime
import icalendar
import os


class TestTime(unittest.TestCase):

    def setUp(self):
        icalendar.cal.types_factory.types_map['X-SOMETIME'] = 'time'

    def tearDown(self):
        icalendar.cal.types_factory.types_map.pop('X-SOMETIME')

    def test_create_from_ical(self):
        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'time.ics'), 'rb')
        cal = icalendar.Calendar.from_ical(ics.read())
        ics.close()

        self.assertEqual(cal['X-SOMETIME'].dt, datetime.time(17, 20, 10))
        self.assertEqual(cal['X-SOMETIME'].to_ical(), '172010')

    def test_create_to_ical(self):
        cal = icalendar.Calendar()
        cal.add('X-SOMETIME', datetime.time(17, 20, 10))
        self.assertTrue(b'X-SOMETIME;VALUE=TIME:172010' in
                        cal.to_ical().splitlines())
