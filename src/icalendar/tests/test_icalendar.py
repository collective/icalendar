# coding: utf-8
import unittest
import doctest
import os
from icalendar import (
    cal,
    caselessdict,
    parser,
    prop,
)

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS


class IcalendarTestCase (unittest.TestCase):

    def test_long_lines(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\r\n')])
        c.append(Contentline(''.join('123456789 ' * 10) + '\r\n'))
        self.assertEqual(
            c.to_ical(),
            'BEGIN:VEVENT\r\n\r\n123456789 123456789 123456789 123456789 '
            '123456789 123456789 123456789 1234\r\n 56789 123456789 '
            '123456789 \r\n\r\n'
        )

    def test_fold_line(self):
        from icalendar.parser import foldline
        self.assertRaises(AssertionError, foldline, u'привет', length=3)
        self.assertEqual(foldline('foobar', length=4), 'foo\r\n bar')
        self.assertEqual(
            foldline('Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                     ' Vestibulum convallis imperdiet dui posuere.'),
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
            ' Vestibulum conval\r\n lis imperdiet dui posuere.'
        )
        self.assertEqual(
            foldline('DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ'),
            'DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭ\r\n ЮЯ'
        )


def load_tests(loader=None, tests=None, pattern=None):
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(caselessdict))
    suite.addTest(doctest.DocTestSuite(parser))
    suite.addTest(doctest.DocTestSuite(prop))
    suite.addTest(doctest.DocTestSuite(cal))
    current_dir = os.path.dirname(__file__)
    for docfile in ['example.txt', 'groupscheduled.txt',
                    'small.txt', 'multiple.txt', 'recurrence.txt']:
        filename = os.path.abspath(os.path.join(current_dir, docfile))
        suite.addTest(
            doctest.DocFileSuite(
                docfile,
                optionflags=OPTIONFLAGS,
                globs={'__file__': filename}
            )
        )
    return suite
