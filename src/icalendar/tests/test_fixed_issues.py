# -*- coding: utf-8 -*-
from . import unittest
import icalendar
import datetime
import os
import pytz

class TestIssues(unittest.TestCase):


    def test_issue_53(self):
        """parsing failure on some descriptions?
        see: https://github.com/collective/icalendar/issues/53
        """

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


    def test_issue_58(self):
        """Issue #58 - TZID on UTC DATE-TIMEs
        https://github.com/collective/icalendar/issues/58
        """

        # According to RFC 2445: "The TZID property parameter MUST NOT be
        # applied to DATE-TIME or TIME properties whose time values are
        # specified in UTC."

        event = icalendar.Event()
        dt = pytz.utc.localize(datetime.datetime(2012,7,16,0,0,0))
        event.add('dtstart', dt)
        self.assertEqual(event.to_ical(),
            "BEGIN:VEVENT\r\n"
            "DTSTART;VALUE=DATE-TIME:20120716T000000Z\r\n"
            "END:VEVENT\r\n")


    def test_issue_64(self):
        """Event.to_ical() fails for unicode strings
        https://github.com/collective/icalendar/issues/64
        """

        # Non-unicode characters
        event = icalendar.Event()
        event.add("dtstart", datetime.datetime(2012,9,3,0,0,0))
        event.add("summary", u"abcdef")
        self.assertEqual(event.to_ical(),
            "BEGIN:VEVENT\r\nSUMMARY:abcdef\r\nDTSTART;VALUE=DATE-TIME:"
            "20120903T000000\r\nEND:VEVENT\r\n")

        # Unicode characters
        event = icalendar.Event()
        event.add("dtstart", datetime.datetime(2012,9,3,0,0,0))
        event.add("summary", u"åäö")
        self.assertEqual(event.to_ical(),
            "BEGIN:VEVENT\r\nSUMMARY:\xc3\xa5\xc3\xa4\xc3\xb6\r\n"
            "DTSTART;VALUE=DATE-TIME:20120903T000000\r\nEND:VEVENT\r\n")


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
