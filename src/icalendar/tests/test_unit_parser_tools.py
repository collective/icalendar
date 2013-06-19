# -*- coding: utf-8 -*-
from . import unittest
from ..parser_tools import to_unicode
from ..parser_tools import data_encode


class TestParserTools(unittest.TestCase):

    def test_parser_tools_to_unicode(self):

        self.assertEqual(to_unicode('spam'), u'spam')
        self.assertEqual(to_unicode(u'spam'), u'spam')
        self.assertEqual(to_unicode(u'spam'.encode('utf-8')), u'spam')
        self.assertEqual(to_unicode('\xc6\xb5'), u'\u01b5')
        self.assertEqual(to_unicode(u'\xc6\xb5'.encode('iso-8859-1')),
                         u'\u01b5')
        self.assertEqual(to_unicode('\xc6\xb5', encoding='ascii'), u'\u01b5')
        self.assertEqual(to_unicode(1), 1)
        self.assertEqual(to_unicode(None), None)

    def test_parser_tools_data_encode(self):

        data1 = {u'k1': u'v1', 'k2': 'v2', u'k3': u'v3',
                'li1': ['it1', u'it2', {'k4': u'v4', u'k5': 'v5'}, 123]}
        res = {'k3': 'v3', 'k2': 'v2', 'k1': 'v1',
               'li1': ['it1', 'it2', {'k5': 'v5', 'k4': 'v4'}, 123]}
        self.assertEqual(data_encode(data1), res)
