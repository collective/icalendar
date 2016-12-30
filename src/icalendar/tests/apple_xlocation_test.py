# -*- coding: utf-8 -*-
from icalendar.tests import unittest

import datetime
import icalendar
import os
import pytz

class TestEncoding(unittest.TestCase):

    def test_apple_xlocation(self):
        """
        Test if we support base64 encoded binary data in parameter values.
        """
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'x_location.ics'), 'rb') as fp:
            data = fp.read()
        cal = icalendar.Calendar.from_ical(data)
        for event in cal.walk('vevent'):
            self.assertEqual(len(event.errors), 0, 'Got too many errors')
