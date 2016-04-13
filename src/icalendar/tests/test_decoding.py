# -*- coding: utf-8 -*-
from icalendar.tests import unittest

import icalendar
import os


def _get_props(item):
    ret = []
    for prop_name, _ in item.items():
        ret.append(item.decoded(prop_name))
    return ret


class DecodeIssues(unittest.TestCase):

    def test_icalendar_1(self):
        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'decoding.ics'), 'rb')
        cal = icalendar.Calendar.from_ical(ics.read())
        ics.close()
        cal.to_ical()
        for item in cal.walk('VEVENT'):
            prop_list = _get_props(item)

    def test_icalendar_2(self):
        directory = os.path.dirname(__file__)
        ics = open(os.path.join(directory, 'decoding2.ics'), 'rb')
        cal = icalendar.Calendar.from_ical(ics.read())
        ics.close()
        cal.to_ical()
        for item in cal.walk('VEVENT'):
            prop_list = _get_props(item)
