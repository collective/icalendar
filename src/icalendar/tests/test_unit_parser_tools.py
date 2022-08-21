from icalendar.parser_tools import data_encode
from icalendar.parser_tools import to_unicode
import unittest


class TestParserTools(unittest.TestCase):

    def test_parser_tools_to_unicode(self):

        self.assertEqual(to_unicode(b'spam'), 'spam')
        self.assertEqual(to_unicode('spam'), 'spam')
        self.assertEqual(to_unicode(b'spam'), 'spam')
        self.assertEqual(to_unicode(b'\xc6\xb5'), '\u01b5')
        self.assertEqual(to_unicode(b'\xc6\xb5'),
                         '\u01b5')
        self.assertEqual(to_unicode(b'\xc6\xb5', encoding='ascii'), '\u01b5')
        self.assertEqual(to_unicode(1), 1)
        self.assertEqual(to_unicode(None), None)

    def test_parser_tools_data_encode(self):

        data1 = {
            'k1': 'v1', 'k2': 'v2', 'k3': 'v3',
            'li1': ['it1', 'it2', {'k4': 'v4', 'k5': 'v5'}, 123]
        }
        res = {b'k3': b'v3', b'k2': b'v2', b'k1': b'v1',
               b'li1': [b'it1', b'it2', {b'k5': b'v5', b'k4': b'v4'}, 123]}
        self.assertEqual(data_encode(data1), res)
