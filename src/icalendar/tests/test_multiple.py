from icalendar import Calendar
from icalendar.prop import vText
from icalendar.tests import unittest

import os


class TestMultiple(unittest.TestCase):
    """A example with multiple VCALENDAR components"""

    def test_multiple(self):

        directory = os.path.dirname(__file__)
        cals = Calendar.from_ical(
            open(os.path.join(directory, 'multiple.ics'), 'rb').read(),
            multiple=True
        )

        self.assertEqual(len(cals), 2)
        self.assertSequenceEqual([comp.name for comp in cals[0].walk()],
                                 ['VCALENDAR', 'VEVENT'])
        self.assertSequenceEqual([comp.name for comp in cals[1].walk()],
                                 ['VCALENDAR', 'VEVENT', 'VEVENT'])

        self.assertEqual(
            cals[0]['prodid'],
            vText('-//Mozilla.org/NONSGML Mozilla Calendar V1.0//EN')
        )
