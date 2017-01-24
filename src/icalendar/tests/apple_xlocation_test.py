# -*- coding: utf-8 -*-
from icalendar.tests import unittest

import datetime
import icalendar
import os
import pytz

class TestEncoding(unittest.TestCase):

    def test_apple_xlocation(self):
        """
        Test if error messages are encode properly.
        """
        try:
            directory = os.path.dirname(__file__)
            with open(os.path.join(directory, 'x_location.ics'), 'rb') as fp:
                data = fp.read()
            cal = icalendar.Calendar.from_ical(data)
            for event in cal.walk('vevent'):
                self.assertEqual(len(event.errors), 1, 'Got too many errors')
                error = event.errors[0][1]
                self.assertTrue(error.startswith(u'Content line could not be parsed into parts'))

        except UnicodeEncodeError as e:
            self.fail("There is something wrong with encoding in the collected error messages")
