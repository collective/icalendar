import doctest
import os.path
from . import unittest


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'example.rst',
    'groupscheduled.rst',
    'multiple.rst',
    'recurrence.rst',
    'small.rst',
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
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
