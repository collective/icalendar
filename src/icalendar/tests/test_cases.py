# -*- coding: utf-8 -*-
import unittest2 as unittest
import icalendar
import os

class TestCases(unittest.TestCase):

    def test_case_meetup(self):
        # broken description
        # see: https://github.com/collective/icalendar/issues/53
        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'case_meetup.ics'),'rb')
        cal = icalendar.Calendar.from_ical(ics.read())
        ics.close()

        event = cal.walk('VEVENT')[0]
        desc = event.get('DESCRIPTION')
        self.assertTrue('July 12 at 6:30 PM' in desc.to_ical())

        timezones = cal.walk('VTIMEZONE')
        self.assertEqual(len(timezones), 1)
        tz = timezones[0]
        self.assertEqual(tz['tzid'].to_ical(), "America/New_York")
