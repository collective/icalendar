import pytest
import unittest

from icalendar.tools import UIDGenerator

class TestTools(unittest.TestCase):

    def test_tools_UIDGenerator(self):

        # Automatic semi-random uid
        g = UIDGenerator()
        uid = g.uid()

        txt = uid.to_ical()
        length = 15 + 1 + 16 + 1 + 11
        self.assertTrue(len(txt) == length)
        self.assertTrue(b'@example.com' in txt)

        # You should at least insert your own hostname to be more compliant
        uid = g.uid('Example.ORG')
        txt = uid.to_ical()
        self.assertTrue(len(txt) == length)
        self.assertTrue(b'@Example.ORG' in txt)

        # You can also insert a path or similar
        uid = g.uid('Example.ORG', '/path/to/content')
        txt = uid.to_ical()
        self.assertTrue(len(txt) == length)
        self.assertTrue(b'-/path/to/content@Example.ORG' in txt)

@pytest.mark.parametrize('host_name, unique', [
    ('example.com', ''),
    ('test.test', ''),
    ('example.com', '123'),
    ('test.test', '123')
])
def test_uid_generator_uses_host_name(host_name, unique):
    '''Issue #345 - Why is tools.UIDGenerator a class (that must be instantiated) instead of a module?

    see https://github.com/collective/icalendar/issues/345
    '''
    uid = UIDGenerator.uid(host_name=host_name, unique=unique)
    assert uid.split('@')[1] == host_name

@pytest.mark.parametrize('host_name, unique', [
    ('example.com', '123'),
    ('test.test', '123')
])
def test_uid_generator_uses_unique(host_name, unique):
    '''Issue #345 - Why is tools.UIDGenerator a class (that must be instantiated) instead of a module?

    see https://github.com/collective/icalendar/issues/345
    '''
    uid = UIDGenerator.uid(host_name=host_name, unique=unique)
    assert uid.split('-')[1] == f'{unique}@{host_name}'
