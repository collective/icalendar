# -*- coding: utf-8 -*-
from icalendar.parser_tools import data_encode
from icalendar.parser_tools import to_unicode
from icalendar.tests import unittest


class TestParserTools(unittest.TestCase):

    def test_parser_tools_to_unicode(self):

        self.assertEqual(to_unicode('spam'), u'spam')
        self.assertEqual(to_unicode(u'spam'), u'spam')
        self.assertEqual(to_unicode(u'spam'.encode('utf-8')), u'spam')
        self.assertEqual(to_unicode(b'\xc6\xb5'), u'\u01b5')
        self.assertEqual(to_unicode(u'\xc6\xb5'.encode('iso-8859-1')),
                         u'\u01b5')
        self.assertEqual(to_unicode(b'\xc6\xb5', encoding='ascii'), u'\u01b5')
        self.assertEqual(to_unicode(1), 1)
        self.assertEqual(to_unicode(None), None)

    def test_parser_tools_data_encode(self):

        data1 = {
            u'k1': u'v1', 'k2': 'v2', u'k3': u'v3',
            'li1': ['it1', u'it2', {'k4': u'v4', u'k5': 'v5'}, 123]
        }
        res = {b'k3': b'v3', b'k2': b'v2', b'k1': b'v1',
               b'li1': [b'it1', b'it2', {b'k5': b'v5', b'k4': b'v4'}, 123]}
        self.assertEqual(data_encode(data1), res)
