# -*- coding: utf-8 -*-

import unittest2 as unittest
import icalendar
import pytz
import datetime
import os

class TestTimezoned(unittest.TestCase):

    def test_create_from_ical(self):
        directory = os.path.dirname(__file__)
        cal = icalendar.Calendar.from_ical(open(os.path.join(directory, 'timezoned.ics'),'rb').read())

        self.assertEqual(cal['prodid'].to_ical(), "-//Plone.org//NONSGML plone.app.event//EN")

        timezones = cal.walk('VTIMEZONE')
        self.assertEqual(len(timezones), 1)

        tz = timezones[0]
        self.assertEqual(tz['tzid'].to_ical(), "Europe/Vienna")

        std = tz.walk('STANDARD')[0]
        self.assertEqual(std.decoded('TZOFFSETFROM'), datetime.timedelta(0, 7200))

        ev1 = cal.walk('VEVENT')[0]
        self.assertEqual(ev1.decoded('DTSTART'), datetime.datetime(2012, 02, 13, 10, 0, 0, tzinfo=pytz.timezone('Europe/Vienna')))
        self.assertEqual(ev1.decoded('DTSTAMP'), datetime.datetime(2010, 10, 10, 9, 10, 10, tzinfo=pytz.utc))

    def test_create_to_ical(self):
        cal = icalendar.Calendar()

        cal.add('prodid', u"-//Plone.org//NONSGML plone.app.event//EN")
        cal.add('version', u"2.0")
        cal.add('x-wr-calname', u"test create calendar")
        cal.add('x-wr-caldesc', u"icalendar tests")
        cal.add('x-wr-relcalid', u"12345")
        cal.add('x-wr-timezone', u"Europe/Vienna")

        event = icalendar.Event()
        tz = pytz.timezone("Europe/Vienna")
        event.add('dtstart', datetime.datetime(2012,02,13,10,00,00,tzinfo=tz))
        event.add('dtend',  datetime.datetime(2012,02,17,18,00,00,tzinfo=tz))
        event.add('dtstamp', datetime.datetime(2010,10,10,10,10,10,tzinfo=tz))
        event.add('created', datetime.datetime(2010,10,10,10,10,10,tzinfo=tz))
        event.add('uid', u'123456')
        event.add('last-modified', datetime.datetime(2010,10,10,10,10,10,tzinfo=tz))
        event.add('summary', u'artsprint 2012')
        #event.add('rrule', u'FREQ=YEARLY;INTERVAL=1;COUNT=10')
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

        ical_lines = cal.to_ical().splitlines()

        self.assertTrue("DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20120213T100000" in ical_lines)
        self.assertTrue("ATTENDEE:sepp" in ical_lines)

        # ical standard expects DTSTAMP and CREATED in UTC
        self.assertTrue("DTSTAMP;VALUE=DATE-TIME:20101010T091010Z" in ical_lines)
        self.assertTrue("CREATED;VALUE=DATE-TIME:20101010T091010Z" in ical_lines)
