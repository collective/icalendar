# -*- coding: utf-8 -*-
import unittest
import icalendar


class TestCalComponent(unittest.TestCase):

    def test_cal_Component(self):
        safe_unicode = icalendar.parser.safe_unicode

        self.assertEqual(safe_unicode('spam'), u'spam')
        self.assertEqual(safe_unicode(u'spam'), u'spam')
        self.assertEqual(safe_unicode(u'spam'.encode('utf-8')), u'spam')
        self.assertEqual(safe_unicode('\xc6\xb5'), u'\u01b5')
        self.assertEqual(safe_unicode(u'\xc6\xb5'.encode('iso-8859-1')),
                         u'\u01b5')
        self.assertEqual(safe_unicode('\xc6\xb5', encoding='ascii'), u'\u01b5')
        self.assertEqual(safe_unicode(1), 1)
        self.assertEqual(safe_unicode(None), None)
