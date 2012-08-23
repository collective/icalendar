# Copyright (c) 2012, Plone Foundation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#from interlude import interact
import unittest, doctest, os
from icalendar import (
    cal,
    caselessdict,
    parser,
    prop,
)


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
            optionflags=doctest.ELLIPSIS,
            globs={'__file__': filename}))
    return suite