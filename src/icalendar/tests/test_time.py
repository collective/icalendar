import unittest2 as unittest
import icalendar
import pytz
import datetime
import os

class TestTime(unittest.TestCase):

    def setUp(self):
        icalendar.cal.types_factory.types_map['X-SOMETIME'] = 'time'

    def tearDown(self):
        icalendar.cal.types_factory.types_map.pop('X-SOMETIME')

    def test_create_from_ical(self):
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'time.ics')) as f:
            cal = icalendar.Calendar.from_ical(f.read())
        self.assertEqual(cal['X-SOMETIME'].dt, datetime.time(17, 20, 10))
        self.assertEqual(cal['X-SOMETIME'].to_ical(), '172010')

    def test_create_to_ical(self):
        cal = icalendar.Calendar()
        cal.add('X-SOMETIME', datetime.time(17, 20, 10))
        self.assertTrue('X-SOMETIME;VALUE=TIME:172010' in
                        cal.to_ical().splitlines())
