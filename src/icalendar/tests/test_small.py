from . import unittest
from ..prop import vText
from icalendar import Calendar
import os

#A small example::
class TestSmall(unittest.TestCase):

    def test_small(self):

        directory = os.path.dirname(__file__)
        cal = Calendar.from_ical(
            open(os.path.join(directory, 'small.ics'),'rb').read())
        self.assertEqual(str(cal), "VCALENDAR({'VERSION': '2.0', "
        "'METHOD': 'Request', "
        "'PRODID': '-//My product//mxm.dk/'})")

        self.assertSequenceEqual([comp.name for comp in cal.walk()],
                                 ['VCALENDAR', 'VEVENT', 'VEVENT'])

        self.assertEqual(str(cal['prodid']), vText('-//My product//mxm.dk/'))

        self.assertEqual(str(cal.decoded('prodid')), '-//My product//mxm.dk/')

        first_event = cal.walk('vevent')[0]
        self.assertEqual(first_event['description'][:75],
        u'This is a very long description that will be folded This is a very long des')

        self.assertEqual(first_event['summary'], vText('A second event'))
