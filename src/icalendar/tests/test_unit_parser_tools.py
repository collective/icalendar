# -*- coding: utf-8 -*-
from . import unittest
from ..parser_tools import to_unicode


class TestParserTools(unittest.TestCase):

    def test_parser_tools_to_unicode(self):

        self.assertEqual(to_unicode('spam'), u'spam')
        self.assertEqual(to_unicode(u'spam'), u'spam')
        self.assertEqual(to_unicode(u'spam'.encode('utf-8')), u'spam')
        self.assertEqual(to_unicode('\xc6\xb5'), u'\u01b5')
        self.assertEqual(to_unicode(u'\xc6\xb5'.encode('iso-8859-1')),
                         u'\u01b5')
        self.assertEqual(to_unicode('\xc6\xb5', encoding='ascii'), u'\u01b5')
        with self.assertRaises(AssertionError):
            to_unicode(1)
        with self.assertRaises(AssertionError):
            to_unicode(None)

