import unittest, doctest, os
from iCalendar import iCalendar, CaselessDict, ContentlinesParser
from iCalendar import PropertyValues, tools

def test_suite():
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocTestSuite(CaselessDict))
    suite.addTest(doctest.DocTestSuite(ContentlinesParser))
    suite.addTest(doctest.DocTestSuite(PropertyValues))
    suite.addTest(doctest.DocTestSuite(iCalendar))
    doc_dir = '../../../doc'
    for docfile in ['example.txt', 'groupscheduled.txt', 'small.txt']:
        suite.addTest(doctest.DocFileSuite(os.path.join(doc_dir, docfile)))
    # only has a disabled doctest
    # suite.addTest(doctest.DocTestSuite(tools))
    return suite
