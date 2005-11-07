import unittest, doctest, os
from icalendar import cal, caselessdict, parser, prop

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(caselessdict))
    suite.addTest(doctest.DocTestSuite(parser))
    suite.addTest(doctest.DocTestSuite(prop))
    suite.addTest(doctest.DocTestSuite(cal))
    doc_dir = '../../../doc'
    for docfile in ['example.txt', 'groupscheduled.txt',
                    'small.txt', 'multiple.txt']:
        suite.addTest(doctest.DocFileSuite(os.path.join(doc_dir, docfile)))
    return suite
