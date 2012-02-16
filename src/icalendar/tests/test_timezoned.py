import unittest2 as unittest
import icalendar
import pytz
import datetime
import os

class TestTimezoned(unittest.TestCase):

    """
    def test_create_from_ical(self):
        directory = os.path.dirname(__file__)
        cal = icalendar.Calendar.from_ical(open(os.path.join(directory, 'timezoned.ics'),'rb').read())

        self.assertTrue(cal, "VCALENDAR({'VERSION': vText(u'2.0'), 'PRODID': vText(u'-//RDU Software//NONSGML HandCal//EN')})")

        timezones = cal.walk('VTIMEZONE')
        self.assertTrue(len(timezones), 1)

        tz = timezones[0]
        self.assertTrue(tz, "VTIMEZONE({'TZID': vText(u'Europe/Vienna')})")

        std = tz.walk('STANDARD')[0]
        self.assertTrue(std.decoded('TZOFFSETFROM'), datetime.timedelta(-1, 72000))
    """

    def test_create_from_code(self):
        cal = icalendar.Calendar()

        cal.add('prodid', u"-//Plone.org//NONSGML plone.app.event//EN")
        cal.add('version', u"2.0")
        cal.add('x-wr-calname', u"test create calendar")
        cal.add('x-wr-caldesc', u"icalendar tests")
        cal.add('x-wr-relcalid', u"12345")
        cal.add('x-wr-timezone', u"Europe/Vienna")

        event = icalendar.Event()
        tz = pytz.timezone("Europe/Vienna")
        event.add('dtstamp', datetime.datetime(2010,10,10,10,10,10,tzinfo=tz))
        event.add('created', datetime.datetime(2010,10,10,10,10,10,tzinfo=tz))
        event.add('uid', u'123456')
        event.add('last-modified', datetime.datetime(2010,10,10,10,10,10,tzinfo=tz))
        event.add('summary', u'artsprint 2012')
        event.add('dtstart', datetime.datetime(2012,02,13,10,00,00,tzinfo=tz))
        event.add('dtend',  datetime.datetime(2012,02,17,18,00,00,tzinfo=tz))
        #event.add('rrule', u'FREQ=YEARLY;INTERVAL=1;COUNT=10')
        event.add('description', u'sprinting at the artsprint')
        event.add('location', u'aka bild, wien')
        event.add('categories', u'first subject')
        event.add('categories', u'second subject')
        event.add('attendee', u'hans')
        event.add('attendee', u'franz')
        event.add('attendee', u'sepp')
        event.add('contact', u'Max Mustermann, 1010 Wien')
        event.add('url', u'http://plone.org')
        cal.add_component(event)

        ical_lines = cal.to_ical().splitlines()

        self.assertTrue("DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20120213T100000" in ical_lines)
        self.assertTrue("ATTENDEE:sepp" in ical_lines)
