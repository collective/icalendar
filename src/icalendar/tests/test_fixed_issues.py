# -*- coding: utf-8 -*-
from . import unittest
import icalendar
import datetime
import os
import pytz


class TestIssues(unittest.TestCase):


    def test_issue_53(self):
        """Issue #53 - Parsing failure on some descriptions?
        https://github.com/collective/icalendar/issues/53
        """

        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'case_meetup.ics'), 'rb')
        cal = icalendar.Calendar.from_ical(ics.read())
        ics.close()

        event = cal.walk('VEVENT')[0]
        desc = event.get('DESCRIPTION')
        self.assertTrue(b'July 12 at 6:30 PM' in desc.to_ical())

        timezones = cal.walk('VTIMEZONE')
        self.assertEqual(len(timezones), 1)
        tz = timezones[0]
        self.assertEqual(tz['tzid'].to_ical(), b"America/New_York")


    def test_issue_55(self):
        """Issue #55 - Parse error on utc-offset with seconds value
        https://github.com/collective/icalendar/issues/55
        """
        ical_str = """BEGIN:VTIMEZONE
TZID:America/Los Angeles
BEGIN:STANDARD
DTSTART:18831118T120702
RDATE:18831118T120702
TZNAME:PST
TZOFFSETFROM:-075258
TZOFFSETTO:-0800
END:STANDARD
END:VTIMEZONE"""

        tz = icalendar.Timezone.from_ical(ical_str)
        self.assertEqual(tz.to_ical(),
            b'BEGIN:VTIMEZONE\r\nTZID:America/Los Angeles\r\nBEGIN:STANDARD\r\n'
            b'DTSTART:18831118T120702\r\nRDATE:18831118T120702\r\nTZNAME:PST'
            b'\r\nTZOFFSETFROM:-075258\r\nTZOFFSETTO:-0800\r\nEND:STANDARD\r\n'
            b'END:VTIMEZONE\r\n')


    def test_issue_58(self):
        """Issue #58 - TZID on UTC DATE-TIMEs
        https://github.com/collective/icalendar/issues/58
        """

        # According to RFC 2445: "The TZID property parameter MUST NOT be
        # applied to DATE-TIME or TIME properties whose time values are
        # specified in UTC."

        event = icalendar.Event()
        dt = pytz.utc.localize(datetime.datetime(2012, 7, 16, 0, 0, 0))
        event.add('dtstart', dt)
        self.assertEqual(event.to_ical(),
            b"BEGIN:VEVENT\r\n"
            b"DTSTART;VALUE=DATE-TIME:20120716T000000Z\r\n"
            b"END:VEVENT\r\n")


    def test_issue_64(self):
        """Issue #64 - Event.to_ical() fails for unicode strings
        https://github.com/collective/icalendar/issues/64
        """

        # Non-unicode characters
        event = icalendar.Event()
        event.add("dtstart", datetime.datetime(2012, 9, 3, 0, 0, 0))
        event.add("summary", u"abcdef")
        self.assertEqual(event.to_ical(),
            b"BEGIN:VEVENT\r\nSUMMARY:abcdef\r\nDTSTART;VALUE=DATE-TIME:"
            b"20120903T000000\r\nEND:VEVENT\r\n")

        # Unicode characters
        event = icalendar.Event()
        event.add("dtstart", datetime.datetime(2012, 9, 3, 0, 0, 0))
        event.add("summary", u"åäö")
        self.assertEqual(event.to_ical(),
            b"BEGIN:VEVENT\r\nSUMMARY:\xc3\xa5\xc3\xa4\xc3\xb6\r\n"
            b"DTSTART;VALUE=DATE-TIME:20120903T000000\r\nEND:VEVENT\r\n")

    def test_issue_70(self):
        """Issue #70 - e.decode("RRULE") causes Attribute Error
        https://github.com/collective/icalendar/issues/70
        """

        ical_str = """BEGIN:VEVENT
CREATED:20081114T072804Z
UID:D449CA84-00A3-4E55-83E1-34B58268853B
DTEND:20070220T180000
RRULE:FREQ=WEEKLY;INTERVAL=1;UNTIL=20070619T225959
TRANSP:OPAQUE
SUMMARY:Esb mellon phone conf
DTSTART:20070220T170000
DTSTAMP:20070221T095412Z
SEQUENCE:0
END:VEVENT"""

        cal = icalendar.Calendar.from_ical(ical_str)
        recur = cal.decoded("RRULE")
        self.assertIsInstance(recur, icalendar.vRecur)
        self.assertEqual(recur.to_ical(),
            b'FREQ=WEEKLY;UNTIL=20070619T225959;INTERVAL=1')



    def test_issue_82(self):
        """Issue #82 - vBinary __repr__ called rather than to_ical from
                       container types
        https://github.com/collective/icalendar/issues/82
        """

        b = icalendar.vBinary('text')
        b.params['FMTTYPE'] = 'text/plain'
        self.assertEqual(b.to_ical(), b'dGV4dA==')
        e = icalendar.Event()
        e.add('ATTACH', b)
        self.assertEqual(e.to_ical(),
            b"BEGIN:VEVENT\r\nATTACH;ENCODING=BASE64;FMTTYPE=text/plain;"
            b"VALUE=BINARY:dGV4dA==\r\nEND:VEVENT\r\n"
        )


    def test_issue_100(self):
        """Issue #100 - Transformed doctests into unittests, Test fixes and
                        cleanup.
        https://github.com/collective/icalendar/pull/100
        """

        ical_content = "BEGIN:VEVENT\r\nSUMMARY;LANGUAGE=ru:te\r\nEND:VEVENT"
        icalendar.Event.from_ical(ical_content).to_ical()


    def test_issue_101(self):
        """Issue #101 - icalender is choking on umlauts in ORGANIZER

        https://github.com/collective/icalendar/issues/101
        """
        ical_str = """BEGIN:VCALENDAR
VERSION:2.0
X-WR-CALNAME:Kalender von acme\, admin
PRODID:-//The Horde Project//Horde_iCalendar Library\, Horde 3.3.5//EN
METHOD:PUBLISH
BEGIN:VEVENT
DTSTART:20130416T100000Z
DTEND:20130416T110000Z
DTSTAMP:20130416T092616Z
UID:20130416112341.10064jz0k4j7uem8@acmenet.de
CREATED:20130416T092341Z
LAST-MODIFIED:20130416T092341Z
SUMMARY:wichtiger termin 1
ORGANIZER;CN="acme, ädmin":mailto:adm-acme@mydomain.de
LOCATION:im büro
CLASS:PUBLIC
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR"""

        cal = icalendar.Calendar.from_ical(ical_str)
        org_cn = cal.walk('VEVENT')[0]['ORGANIZER'].params['CN']
        self.assertEqual(org_cn, u'acme, ädmin')
