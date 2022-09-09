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
            expected_zone = '(UTC-03:00) Brasília'
            expected_tzname = 'Brasília standard'
        except UnicodeEncodeError:
            expected_zone = '(UTC-03:00) Brasília'.encode('ascii', 'replace')
            expected_tzname = 'Brasília standard'.encode('ascii', 'replace')
        self.assertEqual(dtstart.tzinfo.zone, expected_zone)
        self.assertEqual(dtstart.tzname(), expected_tzname)

    def test_issue_345(self):
        """Issue #345 - Why is tools.UIDGenerator a class (that must be instantiated) instead of a module? """
        uid1 = icalendar.tools.UIDGenerator.uid()
        uid2 = icalendar.tools.UIDGenerator.uid('test.test')
        uid3 = icalendar.tools.UIDGenerator.uid(unique='123')
        uid4 = icalendar.tools.UIDGenerator.uid('test.test', '123')

        self.assertEqual(uid1.split('@')[1], 'example.com')
        self.assertEqual(uid2.split('@')[1], 'test.test')
        self.assertEqual(uid3.split('-')[1], '123@example.com')
        self.assertEqual(uid4.split('-')[1], '123@test.test')

@pytest.mark.parametrize("zone", [
    pytz.utc,
    zoneinfo.ZoneInfo('UTC'),
    pytz.timezone('UTC'),
    tz.UTC,
    tz.gettz('UTC')])
def test_issue_335_identify_UTC(zone):
    myevent = icalendar.Event()
    dt = datetime.datetime(2021, 11, 17, 15, 9, 15)
    myevent.add('dtstart', dt.astimezone(zone))
    assert 'DTSTART;VALUE=DATE-TIME:20211117T150915Z' in myevent.to_ical().decode('ASCII')
