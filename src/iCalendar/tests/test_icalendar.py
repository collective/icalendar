import unittest, doctest
from iCalendar import iCalendar, CaselessDict, ContentlinesParser
from iCalendar import PropertyValues, tools

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(CaselessDict))
    suite.addTest(doctest.DocTestSuite(ContentlinesParser))
    suite.addTest(doctest.DocTestSuite(PropertyValues))
    suite.addTest(doctest.DocTestSuite(iCalendar))

    # only has a disabled doctest
    # suite.addTest(doctest.DocTestSuite(tools))
    return suite
