# -*- coding: utf-8 -*-
from icalendar.tests import unittest

import datetime
import icalendar
import os
import pytz

class TestEncoding(unittest.TestCase):

    def test_apple_xlocation(self):
        directory = os.path.dirname(__file__)
        data = open(os.path.join(directory, 'x_location.ics'), 'rb').read()
        cal = icalendar.Calendar.from_ical(data)