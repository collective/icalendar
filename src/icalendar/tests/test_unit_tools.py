import unittest

import pytest

from icalendar.tools import UIDGenerator


class TestTools(unittest.TestCase):
    def test_tools_UIDGenerator(self):
        # Automatic semi-random uid
        g = UIDGenerator()
        uid = g.uid()

        txt = uid.to_ical()
        length = 15 + 1 + 16 + 1 + 11
        self.assertEqual(len(txt), length)
        self.assertIn(b"@example.com", txt)

        # You should at least insert your own hostname to be more compliant
        uid = g.uid("Example.ORG")
        txt = uid.to_ical()
        self.assertEqual(len(txt), length)
        self.assertIn(b"@Example.ORG", txt)

        # You can also insert a path or similar
        uid = g.uid("Example.ORG", "/path/to/content")
        txt = uid.to_ical()
        self.assertEqual(len(txt), length)
        self.assertIn(b"-/path/to/content@Example.ORG", txt)


@pytest.mark.parametrize(
    ("split", "expected", "args", "kw"),
    [
        # default argument host_name
        (
            "@",
            "example.com",
            (),
            {},
        ),
        ("@", "example.com", ("example.com",), {}),
        ("@", "example.com", (), {"host_name": "example.com"}),
        # replaced host_name
        ("@", "test.test", ("test.test",), {}),
        ("@", "test.test", (), {"host_name": "test.test"}),
        # replace unique
        (
            "-",
            "123@example.com",
            (),
            {"unique": "123"},
        ),
        (
            "-",
            "abc@example.com",
            (),
            {"unique": "abc"},
        ),
        # replace host_name and unique
        (
            "-",
            "1234@test.icalendar",
            (),
            {"unique": "1234", "host_name": "test.icalendar"},
        ),
        (
            "-",
            "abc@test.example.com",
            ("test.example.com", "abc"),
            {},
        ),
    ],
)
def test_uid_generator_issue_345(args, kw, split, expected):
    """Issue #345 - Why is tools.UIDGenerator a class (that must be instantiated) instead of a module?

    see https://github.com/collective/icalendar/issues/345
    """
    uid = UIDGenerator.uid(*args, **kw)
    assert uid.split(split)[1] == expected
