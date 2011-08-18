import unittest, doctest, os
from icalendar import cal, caselessdict, parser, prop

class FuckYouTests(unittest.TestCase):
    def XtestBla(self):
        from icalendar import Calendar
        c = Calendar()
        c['description']=u'Paragraph one\n\nParagraph two'
        output = c.as_string()
        self.assertEqual(output, 
                "BEGIN:VCALENDAR\r\nDESCRIPTION:Paragraph one\r\n \r\n Paragraph two\r\nEND:VCALENDAR\r\n")

    def XtestTrailingNewline(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\\r\\n')])
        output = str(c)
        self.assertEqual(output, 'BEGIN:VEVENT\\r\\n')

    def XtestLongLine(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\\r\\n')])
        c.append(Contentline(''.join(['123456789 ']*10)+'\\r\\n'))
        import pdb ; pdb.set_trace()
        output = str(c)
        self.assertEqual(output, 
                "BEGIN:VEVENT\\r\\n\\r\\n123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234\\r\\n 56789 123456789 123456789 \\r\\n")

    def testHmm(self):
        from icalendar.parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT\r\n')])
        c.append(Contentline(''.join(['123456789 ']*10)+'\r\n'))
        output = str(c)
        self.assertEqual(output, 
                'BEGIN:VEVENT\r\n\r\n123456789 123456789 123456789 123456789 123456789 123456789 123456789 1234\r\n 56789 123456789 123456789 \r\n')

def load_tests(loader=None, tests=None, pattern=None):

    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(caselessdict))
    suite.addTest(doctest.DocTestSuite(parser))
    suite.addTest(doctest.DocTestSuite(prop))
    suite.addTest(doctest.DocTestSuite(cal))

    current_dir = os.path.dirname(__file__)
    for docfile in ['example.txt', 'groupscheduled.txt',
                    'small.txt', 'multiple.txt', 'recurrence.txt']:
        suite.addTest(doctest.DocFileSuite(docfile,
            optionflags=doctest.ELLIPSIS,
            globs={'__file__': os.path.abspath(os.path.join(current_dir, docfile))},
                ))

    return suite
