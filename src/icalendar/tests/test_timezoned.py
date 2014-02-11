# -*- coding: utf-8 -*-
from icalendar.tests import unittest

import datetime
import dateutil.parser
import icalendar
import os
import pytz


class TestTimezoned(unittest.TestCase):

    def test_create_from_ical(self):
        directory = os.path.dirname(__file__)
        cal = icalendar.Calendar.from_ical(
            open(os.path.join(directory, 'timezoned.ics'), 'rb').read()
        )

        self.assertEqual(
            cal['prodid'].to_ical(),
            b"-//Plone.org//NONSGML plone.app.event//EN"
        )

        timezones = cal.walk('VTIMEZONE')
        self.assertEqual(len(timezones), 1)

        tz = timezones[0]
        self.assertEqual(tz['tzid'].to_ical(), b"Europe/Vienna")

        std = tz.walk('STANDARD')[0]
        self.assertEqual(
            std.decoded('TZOFFSETFROM'),
            datetime.timedelta(0, 7200)
        )

        ev1 = cal.walk('VEVENT')[0]
        self.assertEqual(
            ev1.decoded('DTSTART'),
            datetime.datetime(2012, 2, 13, 10, 0, 0,
                              tzinfo=pytz.timezone('Europe/Vienna')))
        self.assertEqual(
            ev1.decoded('DTSTAMP'),
            datetime.datetime(2010, 10, 10, 9, 10, 10, tzinfo=pytz.utc))

    def test_create_to_ical(self):
        cal = icalendar.Calendar()

        cal.add('prodid', u"-//Plone.org//NONSGML plone.app.event//EN")
        cal.add('version', u"2.0")
        cal.add('x-wr-calname', u"test create calendar")
        cal.add('x-wr-caldesc', u"icalendar tests")
        cal.add('x-wr-relcalid', u"12345")
        cal.add('x-wr-timezone', u"Europe/Vienna")

        tzc = icalendar.Timezone()
        tzc.add('tzid', 'Europe/Vienna')
        tzc.add('x-lic-location', 'Europe/Vienna')

        tzs = icalendar.TimezoneStandard()
        tzs.add('tzname', 'CET')
        tzs.add('dtstart', datetime.datetime(1970, 10, 25, 3, 0, 0))
        tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
        tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
        tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))

        tzd = icalendar.TimezoneDaylight()
        tzd.add('tzname', 'CEST')
        tzd.add('dtstart', datetime.datetime(1970, 3, 29, 2, 0, 0))
        tzs.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
        tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
        tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

        tzc.add_component(tzs)
        tzc.add_component(tzd)
        cal.add_component(tzc)

        event = icalendar.Event()
        tz = pytz.timezone("Europe/Vienna")
        event.add(
            'dtstart',
            datetime.datetime(2012, 2, 13, 10, 00, 00, tzinfo=tz))
        event.add(
            'dtend',
            datetime.datetime(2012, 2, 17, 18, 00, 00, tzinfo=tz))
        event.add(
            'dtstamp',
            datetime.datetime(2010, 10, 10, 10, 10, 10, tzinfo=tz))
        event.add(
            'created',
            datetime.datetime(2010, 10, 10, 10, 10, 10, tzinfo=tz))
        event.add('uid', u'123456')
        event.add(
            'last-modified',
            datetime.datetime(2010, 10, 10, 10, 10, 10, tzinfo=tz))
        event.add('summary', u'artsprint 2012')
        # event.add('rrule', u'FREQ=YEARLY;INTERVAL=1;COUNT=10')
        event.add('description', u'sprinting at the artsprint')
        event.add('location', u'aka bild, wien')
        event.add('categories', u'first subject')
        event.add('categories', u'second subject')
        event.add('attendee', u'häns')
        event.add('attendee', u'franz')
        event.add('attendee', u'sepp')
        event.add('contact', u'Max Mustermann, 1010 Wien')
        event.add('url', u'http://plone.org')
        cal.add_component(event)

        test_out = b'|'.join(cal.to_ical().splitlines())
        test_out = test_out.decode('utf-8')

        vtimezone_lines = "BEGIN:VTIMEZONE|TZID:Europe/Vienna|X-LIC-LOCATION:"
        "Europe/Vienna|BEGIN:STANDARD|DTSTART;VALUE=DATE-TIME:19701025T03"
        "0000|RRULE:FREQ=YEARLY;BYDAY=-1SU;BYMONTH=10|RRULE:FREQ=YEARLY;B"
        "YDAY=-1SU;BYMONTH=3|TZNAME:CET|TZOFFSETFROM:+0200|TZOFFSETTO:+01"
        "00|END:STANDARD|BEGIN:DAYLIGHT|DTSTART;VALUE=DATE-TIME:19700329T"
        "020000|TZNAME:CEST|TZOFFSETFROM:+0100|TZOFFSETTO:+0200|END:DAYLI"
        "GHT|END:VTIMEZONE"
        self.assertTrue(vtimezone_lines in test_out)

        test_str = "DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20120213T100000"
        self.assertTrue(test_str in test_out)
        self.assertTrue("ATTENDEE:sepp" in test_out)

        # ical standard expects DTSTAMP and CREATED in UTC
        self.assertTrue("DTSTAMP;VALUE=DATE-TIME:20101010T091010Z" in test_out)
        self.assertTrue("CREATED;VALUE=DATE-TIME:20101010T091010Z" in test_out)

    def test_tzinfo_dateutil(self):
        # Test for issues #77, #63
        # references: #73,7430b66862346fe3a6a100ab25e35a8711446717

        date = dateutil.parser.parse('2012-08-30T22:41:00Z')
        date2 = dateutil.parser.parse('2012-08-30T22:41:00 +02:00')
        self.assertTrue(date.tzinfo.__module__ == 'dateutil.tz')
        self.assertTrue(date2.tzinfo.__module__ == 'dateutil.tz')

        # make sure, it's parsed properly and doesn't throw an error
        self.assertTrue(icalendar.vDDDTypes(date).to_ical()
                        == b'20120830T224100Z')
        self.assertTrue(icalendar.vDDDTypes(date2).to_ical()
                        == b'20120830T224100')
