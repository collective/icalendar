#from interlude import interact
import unittest, doctest, os
from icalendar import (
    cal,
    caselessdict,
    parser,
    prop,
)

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

class FuckYouTests(unittest.TestCase):
    def XtestBla(self):
        from icalendar import Calendar
        c = Calendar()
        c['description']=u'Paragraph one\n\nParagraph two'
        output = c.to_ical()
        cmp = ("BEGIN:VCALENDAR\r\nDESCRIPTION:Paragraph one\r\n \r\n "
               "Paragraph two\r\nEND:VCALENDAR\r\n")
        self.assertEqual(output, cmp)

    def XtestTrailingNewline(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\\r\\n')])
        output = c.to_ical()
        self.assertEqual(output, 'BEGIN:VEVENT\\r\\n')

    def XtestLongLine(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\\r\\n')])
        c.append(Contentline(''.join(['123456789 ']*10)+'\\r\\n'))
        output = c.to_ical()
        cmp = ("BEGIN:VEVENT\\r\\n\\r\\n123456789 123456789 123456789 "
               "123456789 123456789 123456789 123456789 1234\\r\\n 56789 "
               "123456789 123456789 \\r\\n")
        self.assertEqual(output, cmp)

    def testHmm(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\r\n')])
        c.append(Contentline(''.join(['123456789 ']*10)+'\r\n'))
        output = c.to_ical()
        # XXX: sure? looks weird in conjunction with generated content above.
        #cmp = ('BEGIN:VEVENT\r\n\r\n123456789 123456789 123456789 123456789 '
        #       '123456789 123456789 123456789 1234\r\n 56789 123456789 '
        #       '123456789 \r\n')
        cmp = ('BEGIN:VEVENT\r\n\r\n123456789 123456789 123456789 123456789 '
               '123456789 123456789 123456789 \r\n 123456789 123456789 '
               '123456789 \r\n\r\n')
        self.assertEqual(output, cmp)


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
        suite.addTest(doctest.DocFileSuite(docfile,
            optionflags=OPTIONFLAGS,
            globs={'__file__': filename}))
    return suite
