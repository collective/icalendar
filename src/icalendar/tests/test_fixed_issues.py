import unittest

import datetime
import icalendar
import os
import pytz
import pytest
from dateutil import tz

try:
    import zoneinfo
except ModuleNotFoundError:
    from backports import zoneinfo

class TestIssues(unittest.TestCase):
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
        self.assertEqual(
            tz.to_ical(),
            b'BEGIN:VTIMEZONE\r\nTZID:America/Los Angeles\r\n'
            b'BEGIN:STANDARD\r\n'
            b'DTSTART:18831118T120702\r\nRDATE:18831118T120702\r\nTZNAME:PST'
            b'\r\nTZOFFSETFROM:-075258\r\nTZOFFSETTO:-0800\r\n'
            b'END:STANDARD\r\n'
            b'END:VTIMEZONE\r\n')

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
        self.assertEqual(
            recur.to_ical(),
            b'FREQ=WEEKLY;UNTIL=20070619T225959;INTERVAL=1'
        )

    def test_issue_100(self):
        """Issue #100 - Transformed doctests into unittests, Test fixes and
                        cleanup.
        https://github.com/collective/icalendar/pull/100
        """

        ical_content = "BEGIN:VEVENT\r\nSUMMARY;LANGUAGE=ru:te\r\nEND:VEVENT"
        icalendar.Event.from_ical(ical_content).to_ical()

    def test_issue_184(self):
        """Issue #184 - Previous changes in code broke already broken
        representation of PERIOD values - in a new way"""

        ical_str = ['BEGIN:VEVENT',
                    'DTSTAMP:20150219T133000',
                    'DTSTART:20150219T133000',
                    'UID:1234567',
                    'RDATE;VALUE=PERIOD:20150219T133000/PT10H',
                    'END:VEVENT']

        event = icalendar.Event.from_ical('\r\n'.join(ical_str))
        self.assertEqual(event.errors, [])
        self.assertEqual(event.to_ical(),
                         b'BEGIN:VEVENT\r\nDTSTART:20150219T133000\r\n'
                         b'DTSTAMP:20150219T133000\r\nUID:1234567\r\n'
                         b'RDATE;VALUE=PERIOD:20150219T133000/PT10H\r\n'
                         b'END:VEVENT\r\n'
                         )

    def test_issue_237(self):
        """Issue #237 - Fail to parse timezone with non-ascii TZID"""

        ical_str = ['BEGIN:VCALENDAR',
                    'BEGIN:VTIMEZONE',
                    'TZID:(UTC-03:00) Brasília',
                    'BEGIN:STANDARD',
                    'TZNAME:Brasília standard',
                    'DTSTART:16010101T235959',
                    'TZOFFSETFROM:-0200',
                    'TZOFFSETTO:-0300',
                    'RRULE:FREQ=YEARLY;INTERVAL=1;BYDAY=3SA;BYMONTH=2',
                    'END:STANDARD',
                    'BEGIN:DAYLIGHT',
                    'TZNAME:Brasília daylight',
                    'DTSTART:16010101T235959',
                    'TZOFFSETFROM:-0300',
                    'TZOFFSETTO:-0200',
                    'RRULE:FREQ=YEARLY;INTERVAL=1;BYDAY=2SA;BYMONTH=10',
                    'END:DAYLIGHT',
                    'END:VTIMEZONE',
                    'BEGIN:VEVENT',
                    'DTSTART;TZID=\"(UTC-03:00) Brasília\":20170511T133000',
                    'DTEND;TZID=\"(UTC-03:00) Brasília\":20170511T140000',
                    'END:VEVENT',
                    'END:VCALENDAR',
                    ]

        cal = icalendar.Calendar.from_ical('\r\n'.join(ical_str))
        self.assertEqual(cal.errors, [])

        dtstart = cal.walk(name='VEVENT')[0].decoded("DTSTART")
        expected = pytz.timezone('America/Sao_Paulo').localize(datetime.datetime(2017, 5, 11, 13, 30))
        self.assertEqual(dtstart, expected)

        try:
            expected_zone = '(UTC-03:00) Brasília'
            expected_tzname = 'Brasília standard'
        except UnicodeEncodeError:
            expected_zone = '(UTC-03:00) Brasília'.encode('ascii', 'replace')
            expected_tzname = 'Brasília standard'.encode('ascii', 'replace')
        self.assertEqual(dtstart.tzinfo.zone, expected_zone)
        self.assertEqual(dtstart.tzname(), expected_tzname)

