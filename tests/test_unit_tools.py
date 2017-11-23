# -*- coding: utf-8 -*-
import unittest
from icalendar.tools import UIDGenerator


class TestTools(unittest.TestCase):

    def test_tools_UIDGenerator(self):

        # Automatic semi-random uid
        g = UIDGenerator()
        uid = g.uid()

        txt = uid.to_ical()
        length = 15 + 1 + 16 + 1 + 11
        self.assertTrue(len(txt) == length)
        self.assertTrue(b'@example.com' in txt)

        # You should at least insert your own hostname to be more compliant
        uid = g.uid('Example.ORG')
        txt = uid.to_ical()
        self.assertTrue(len(txt) == length)
        self.assertTrue(b'@Example.ORG' in txt)

        # You can also insert a path or similar
        uid = g.uid('Example.ORG', '/path/to/content')
        txt = uid.to_ical()
        self.assertTrue(len(txt) == length)
        self.assertTrue(b'-/path/to/content@Example.ORG' in txt)
