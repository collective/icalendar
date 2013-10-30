from . import unittest
from icalendar import Calendar
import datetime
import os

# An example from the RFC 2445 spec::

class TestGroupScheduled(unittest.TestCase):

    def test_group_schedule(self):

        directory = os.path.dirname(__file__)
        cal = Calendar.from_ical(
        open(os.path.join(directory, 'groupscheduled.ics'),'rb').read())

        self.assertEqual(str(cal),
  "VCALENDAR({'VERSION': '2.0', 'PRODID': '-//RDU Software//NONSGML HandCal//EN'})")

        timezones = cal.walk('VTIMEZONE')
        self.assertEqual(len(timezones), 1)

        tz = timezones[0]
        self.assertEqual(str(tz), "VTIMEZONE({'TZID': 'US-Eastern'})")

        std = tz.walk('STANDARD')[0]
        self.assertEqual(std.decoded('TZOFFSETFROM'), datetime.timedelta(-1, 72000))
