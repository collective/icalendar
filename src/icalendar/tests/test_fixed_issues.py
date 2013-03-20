# -*- coding: utf-8 -*-
from . import unittest
import icalendar
import os

class TestIssues(unittest.TestCase):

    def test_issue_53(self):
        # parsing failure on some descriptions?
        # see: https://github.com/collective/icalendar/issues/53
        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'case_meetup.ics'), 'rb')
        cal = icalendar.Calendar.from_ical(ics.read())
        ics.close()

        event = cal.walk('VEVENT')[0]
        desc = event.get('DESCRIPTION')
        self.assertTrue('July 12 at 6:30 PM' in desc.to_ical())

        timezones = cal.walk('VTIMEZONE')
        self.assertEqual(len(timezones), 1)
        tz = timezones[0]
        self.assertEqual(tz['tzid'].to_ical(), "America/New_York")

    def test_issue_82(self):
        # vBinary __repr__ called rather than to_ical from container types
        # https://github.com/collective/icalendar/issues/82
        b = icalendar.vBinary('text')
        b.params['FMTTYPE'] = 'text/plain'
        self.assertEqual(b.to_ical(), 'dGV4dA==')
        e = icalendar.Event()
        e.add('ATTACH', b)
        self.assertEqual(e.to_ical(),
            "BEGIN:VEVENT\r\nATTACH;ENCODING=BASE64;FMTTYPE=text/plain;"
            "VALUE=BINARY:dGV4dA==\r\nEND:VEVENT\r\n"
        )
