import unittest
import icalendar


class TestCaselessdict(unittest.TestCase):

    def test_caselessdict_canonsort_keys(self):
        canonsort_keys = icalendar.caselessdict.canonsort_keys

        keys = ['DTEND', 'DTSTAMP', 'DTSTART', 'UID', 'SUMMARY', 'LOCATION']

        out = canonsort_keys(keys)
        self.assertEqual(out,
            ['DTEND', 'DTSTAMP', 'DTSTART', 'LOCATION', 'SUMMARY', 'UID'])

        out = canonsort_keys(keys, ('SUMMARY', 'DTSTART', 'DTEND', ))
        self.assertEqual(out,
            ['SUMMARY', 'DTSTART', 'DTEND', 'DTSTAMP', 'LOCATION', 'UID'])

        out = canonsort_keys(keys, ('UID', 'DTSTART', 'DTEND', ))
        self.assertEqual(out,
            ['UID', 'DTSTART', 'DTEND', 'DTSTAMP', 'LOCATION', 'SUMMARY'])

        out = canonsort_keys(keys,
            ('UID', 'DTSTART', 'DTEND', 'RRULE', 'EXDATE'))
        self.assertEqual(out,
            ['UID', 'DTSTART', 'DTEND', 'DTSTAMP', 'LOCATION', 'SUMMARY'])


    def test_caselessdict_canonsort_items(self):
        canonsort_items = icalendar.caselessdict.canonsort_items

        d = dict(i=7, c='at', a=3.5, l=(2,3), e=[4,5], n=13, d={'x': 'y'},
                 r=1.0)

        out = canonsort_items(d)
        self.assertEqual(out,
            [('a', 3.5), ('c', 'at'), ('d', {'x': 'y'}), ('e', [4, 5]),
             ('i', 7), ('l', (2, 3)), ('n', 13), ('r', 1.0)])

        out = canonsort_items(d, ('i', 'c', 'a'))
        self.assertTrue(out,
            [('i', 7), ('c', 'at'), ('a', 3.5), ('d', {'x': 'y'}),
             ('e', [4, 5]), ('l', (2, 3)), ('n', 13), ('r', 1.0)])
