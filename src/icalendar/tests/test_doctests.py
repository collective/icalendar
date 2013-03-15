import doctest
import os.path
import unittest


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'example.rst',
    'groupscheduled.rst',
    'multiple.rst',
    'recurrence.rst',
    'small.rst',
    'issues.rst',
]
DOCMODS = [
    'icalendar.caselessdict',
    'icalendar.cal',
    'icalendar.parser',
    'icalendar.prop',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            os.path.join(os.path.dirname(__file__), docfile),
            module_relative=False,
            optionflags=OPTIONFLAGS,
        ) for docfile in DOCFILES
    ])
    suite.addTests([
        doctest.DocTestSuite(
            docmod,
            optionflags=OPTIONFLAGS,
        ) for docmod in DOCMODS
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
