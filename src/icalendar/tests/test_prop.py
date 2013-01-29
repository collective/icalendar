import datetime
import unittest

import icalendar
import pytz


class TestPropertyValues(unittest.TestCase):

    def test_vDDDLists_timezone(self):
        """Test vDDDLists with timezone information.
        """
        e = icalendar.Event()
        at = pytz.timezone('Europe/Vienna')
        dt1 = at.localize(datetime.datetime(2013,1,1))
        dt2 = at.localize(datetime.datetime(2013,1,2))
        dt3 = at.localize(datetime.datetime(2013,1,3))
        e.add('rdate', [dt1, dt2])
        e.add('exdate', dt3)
        out = e.to_ical()

        self.assertTrue('RDATE;TZID=Europe/Vienna:20130101T000000,20130102T000000' in out)
        self.assertTrue('EXDATE;TZID=Europe/Vienna:20130103T000000' in out)

        #'BEGIN:VEVENT\r\nDTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130101T000000\r\nRDATE;TZID=Europe/Vienna:20130101T000000,20130102T000000\r\nEXDATE;TZID=Europe/Vienna:20130103T000000\r\nEND:VEVENT\r\n'
