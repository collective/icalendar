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
        self.assertEqual(
            e.to_ical(),
            b"BEGIN:VEVENT\r\nATTACH;ENCODING=BASE64;FMTTYPE=text/plain;"
            b"VALUE=BINARY:dGV4dA==\r\nEND:VEVENT\r\n"
        )

    def test_issue_116(self):
        """Issue #116/#117 - How to add 'X-APPLE-STRUCTURED-LOCATION'
        https://github.com/collective/icalendar/issues/116
        https://github.com/collective/icalendar/issues/117
        """
        event = icalendar.Event()
        event.add(
            "X-APPLE-STRUCTURED-LOCATION",
            "geo:-33.868900,151.207000",
            parameters={
                "VALUE": "URI",
                "X-ADDRESS": "367 George Street Sydney CBD NSW 2000",
                "X-APPLE-RADIUS": "72",
                "X-TITLE": "367 George Street"
            }
        )
        self.assertEqual(
            event.to_ical(),
            b'BEGIN:VEVENT\r\nX-APPLE-STRUCTURED-LOCATION;VALUE=URI;'
            b'X-ADDRESS="367 George Street Sydney \r\n CBD NSW 2000";'
            b'X-APPLE-RADIUS=72;X-TITLE="367 George Street":'
            b'geo:-33.868900\r\n \\,151.207000\r\nEND:VEVENT\r\n'
        )

        # roundtrip
        self.assertEqual(
            event.to_ical(),
            icalendar.Event.from_ical(event.to_ical()).to_ical()
        )

    def test_issue_142(self):
        """Issue #142 - Multivalued parameters
        This is needed for VCard 3.0.
        https://github.com/collective/icalendar/pull/142
        """
        from icalendar.parser import Contentline, Parameters

        ctl = Contentline.from_ical("TEL;TYPE=HOME,VOICE:000000000")

        self.assertEqual(
            ctl.parts(),
            ('TEL', Parameters({'TYPE': ['HOME', 'VOICE']}), '000000000'),
        )

    def test_issue_143(self):
        """Issue #143 - Allow dots in property names.
        Another vCard related issue.
        https://github.com/collective/icalendar/pull/143
        """
        from icalendar.parser import Contentline, Parameters

        ctl = Contentline.from_ical("ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR:;;This is the Adress 08; Some City;;12345;Germany")  # nopep8
        self.assertEqual(
            ctl.parts(),
            ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR',
             Parameters(),
             ';;This is the Adress 08; Some City;;12345;Germany'),
        )

        ctl2 = Contentline.from_ical("ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.X-ABLABEL:")  # nopep8
        self.assertEqual(
            ctl2.parts(),
            ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.X-ABLABEL',
             Parameters(),
             ''),
        )

    def test_issue_168(self):
        """Issue #168 - Parsing invalid icalendars fails without any warning
        https://github.com/collective/icalendar/issues/168
        """

        event_str = """
BEGIN:VCALENDAR
BEGIN:VEVENT
DTEND:20150905T100000Z
DTSTART:20150905T090000Z
X-APPLE-RADIUS=49.91307046514149
UID:123
END:VEVENT
END:VCALENDAR"""

        calendar = icalendar.Calendar.from_ical(event_str)
        self.assertEqual(
            calendar.to_ical(),
            b'BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDTSTART:20150905T090000Z\r\n'
            b'DTEND:20150905T100000Z\r\nUID:123\r\n'
            b'END:VEVENT\r\nEND:VCALENDAR\r\n'
        )

    def test_issue_178(self):
        """Issue #178 - A component with an unknown/invalid name is represented
        as one of the known components, the information about the original
        component name is lost.
        https://github.com/collective/icalendar/issues/178
        https://github.com/collective/icalendar/pull/180
        """

        # Parsing of a nonstandard component
        ical_str = '\r\n'.join(['BEGIN:MYCOMP', 'END:MYCOMP'])
        cal = icalendar.Calendar.from_ical(ical_str)
        self.assertEqual(cal.to_ical(),
                         b'BEGIN:MYCOMP\r\nEND:MYCOMP\r\n')

        # Nonstandard component inside other components, also has properties
        ical_str = '\r\n'.join(['BEGIN:VCALENDAR',
                                'BEGIN:UNKNOWN',
                                'UID:1234',
                                'END:UNKNOWN',
                                'END:VCALENDAR'])

        cal = icalendar.Calendar.from_ical(ical_str)
        self.assertEqual(cal.errors, [])
        self.assertEqual(cal.to_ical(),
                         b'BEGIN:VCALENDAR\r\nBEGIN:UNKNOWN\r\nUID:1234\r\n'
                         b'END:UNKNOWN\r\nEND:VCALENDAR\r\n')

        # Nonstandard component is able to contain other components
        ical_str = '\r\n'.join(['BEGIN:MYCOMPTOO',
                                'DTSTAMP:20150121T080000',
                                'BEGIN:VEVENT',
                                'UID:12345',
                                'DTSTART:20150122',
                                'END:VEVENT',
                                'END:MYCOMPTOO'])
        cal = icalendar.Calendar.from_ical(ical_str)
        self.assertEqual(cal.errors, [])
        self.assertEqual(cal.to_ical(),
                         b'BEGIN:MYCOMPTOO\r\nDTSTAMP:20150121T080000\r\n'
                         b'BEGIN:VEVENT\r\nDTSTART:20150122\r\nUID:12345\r\n'
                         b'END:VEVENT\r\nEND:MYCOMPTOO\r\n')

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
