import unittest
import icalendar


class TestProp(unittest.TestCase):

    def test_prop_vBinary(self):
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
