# -*- coding: utf-8 -*-
from icalendar import Calendar
from icalendar.prop import vText
import unittest

import os


class TestMultiple(unittest.TestCase):
    """A example with multiple VCALENDAR components"""

    def test_multiple(self):

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'multiple.ics'), 'rb') as fp:
            data = fp.read()
        cals = Calendar.from_ical(data, multiple=True)

        self.assertEqual(len(cals), 2)
        self.assertSequenceEqual([comp.name for comp in cals[0].walk()],
                                 ['VCALENDAR', 'VEVENT'])
        self.assertSequenceEqual([comp.name for comp in cals[1].walk()],
                                 ['VCALENDAR', 'VEVENT', 'VEVENT'])

        self.assertEqual(
            cals[0]['prodid'],
            vText('-//Mozilla.org/NONSGML Mozilla Calendar V1.0//EN')
        )
