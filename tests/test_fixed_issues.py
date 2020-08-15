# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from icalendar.parser_tools import to_unicode
import unittest

import datetime
import icalendar
import os
import pytz


class TestIssues(unittest.TestCase):

    def test_issue_53(self):
        """Issue #53 - Parsing failure on some descriptions?
        https://github.com/collective/icalendar/issues/53
        """

        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'issue_53_parsing_failure.ics'),
                   'rb')
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
        self.assertEqual(
            tz.to_ical(),
            b'BEGIN:VTIMEZONE\r\nTZID:America/Los Angeles\r\n'
            b'BEGIN:STANDARD\r\n'
            b'DTSTART:18831118T120702\r\nRDATE:18831118T120702\r\nTZNAME:PST'
            b'\r\nTZOFFSETFROM:-075258\r\nTZOFFSETTO:-0800\r\n'
            b'END:STANDARD\r\n'
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
        self.assertEqual(
            event.to_ical(),
            b"BEGIN:VEVENT\r\n"
            b"DTSTART;VALUE=DATE-TIME:20120716T000000Z\r\n"
            b"END:VEVENT\r\n"
        )

    def test_issue_64(self):
        """Issue #64 - Event.to_ical() fails for unicode strings
        https://github.com/collective/icalendar/issues/64
        """

        # Non-unicode characters
        event = icalendar.Event()
        event.add("dtstart", datetime.datetime(2012, 9, 3, 0, 0, 0))
        event.add("summary", "abcdef")
        self.assertEqual(
            event.to_ical(),
            b"BEGIN:VEVENT\r\nSUMMARY:abcdef\r\nDTSTART;VALUE=DATE-TIME:"
            b"20120903T000000\r\nEND:VEVENT\r\n"
        )

        # Unicode characters
        event = icalendar.Event()
        event.add("dtstart", datetime.datetime(2012, 9, 3, 0, 0, 0))
        event.add("summary", "åäö")
        self.assertEqual(
            event.to_ical(),
            b"BEGIN:VEVENT\r\nSUMMARY:\xc3\xa5\xc3\xa4\xc3\xb6\r\n"
            b"DTSTART;VALUE=DATE-TIME:20120903T000000\r\nEND:VEVENT\r\n"
        )

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
        ical_str = r"""BEGIN:VCALENDAR
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
        self.assertEqual(org_cn, 'acme, ädmin')

    def test_issue_104__ignore_exceptions(self):
        """
        Issue #104 - line parsing error in a VEVENT
        (which has ignore_exceptions). Should mark the event broken
        but not raise an exception.
        https://github.com/collective/icalendar/issues/104
        """
        ical_str = """
BEGIN:VEVENT
DTSTART:20140401T000000Z
DTEND:20140401T010000Z
DTSTAMP:20140401T000000Z
SUMMARY:Broken Eevnt
CLASS:PUBLIC
STATUS:CONFIRMED
TRANSP:OPAQUE
X
END:VEVENT"""
        event = icalendar.Calendar.from_ical(ical_str)
        self.assertTrue(isinstance(event, icalendar.Event))
        self.assertTrue(event.is_broken)  # REMOVE FOR NEXT MAJOR RELEASE
        self.assertEqual(
            event.errors,
            [(None, "Content line could not be parsed into parts: 'X': Invalid content line")]  # noqa
        )

    def test_issue_104__no_ignore_exceptions(self):
        """
        Issue #104 - line parsing error in a VCALENDAR
        (which doesn't have ignore_exceptions). Should raise an exception.
        """
        ical_str = """BEGIN:VCALENDAR
VERSION:2.0
METHOD:PUBLISH
BEGIN:VEVENT
DTSTART:20140401T000000Z
DTEND:20140401T010000Z
DTSTAMP:20140401T000000Z
SUMMARY:Broken Eevnt
CLASS:PUBLIC
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
X
END:VCALENDAR"""
        with self.assertRaises(ValueError):
            icalendar.Calendar.from_ical(ical_str)

    def test_issue_112(self):
        """Issue #112 - No timezone info on EXDATE
        https://github.com/collective/icalendar/issues/112
        """
        directory = os.path.dirname(__file__)
        path = os.path.join(directory,
                            'issue_112_missing_tzinfo_on_exdate.ics')
        with open(path, 'rb') as ics:
            cal = icalendar.Calendar.from_ical(ics.read())
            event = cal.walk('VEVENT')[0]

            event_ical = to_unicode(event.to_ical())  # Py3 str type doesn't
                                                      # support buffer API
            # General timezone aware dates in ical string
            self.assertTrue('DTSTART;TZID=America/New_York:20130907T120000'
                            in event_ical)
            self.assertTrue('DTEND;TZID=America/New_York:20130907T170000'
                            in event_ical)
            # Specific timezone aware exdates in ical string
            self.assertTrue('EXDATE;TZID=America/New_York:20131012T120000'
                            in event_ical)
            self.assertTrue('EXDATE;TZID=America/New_York:20131011T120000'
                            in event_ical)

            self.assertEqual(event['exdate'][0].dts[0].dt.tzname(), 'EDT')

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

    def test_issue_157(self):
        """Issue #157 - Recurring rules and trailing semicolons
        https://github.com/collective/icalendar/pull/157
        """
        # The trailing semicolon caused a problem
        ical_str = """BEGIN:VEVENT
DTSTART:20150325T101010
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU;
END:VEVENT"""

        cal = icalendar.Calendar.from_ical(ical_str)
        recur = cal.decoded("RRULE")
        self.assertIsInstance(recur, icalendar.vRecur)
        self.assertEqual(
            recur.to_ical(),
            b'FREQ=YEARLY;BYDAY=1SU;BYMONTH=11'
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

    def test_index_error_issue(self):
        """Found an issue where from_ical() would raise IndexError for
        properties without parent components.
        https://github.com/collective/icalendar/pull/179
        """

        with self.assertRaises(ValueError):
            icalendar.Calendar.from_ical('VERSION:2.0')

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
            expected_zone = str('(UTC-03:00) Brasília')
            expected_tzname = str('Brasília standard')
        except UnicodeEncodeError:
            expected_zone = '(UTC-03:00) Brasília'.encode('ascii', 'replace')
            expected_tzname = 'Brasília standard'.encode('ascii', 'replace')
        self.assertEqual(dtstart.tzinfo.zone, expected_zone)
        self.assertEqual(dtstart.tzname(), expected_tzname)
