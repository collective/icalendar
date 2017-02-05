import string

from hypothesis import given, settings
import hypothesis.strategies as st

from icalendar.parser import Contentline, Contentlines, Parameters
from icalendar.tests import unittest


def printable_characters(**kw):
    return st.text(
        st.characters(blacklist_categories=(
            'Cc', 'Cs'
        ), **kw)
    )

key = st.text(string.ascii_letters + string.digits, min_size=1)
value = printable_characters(blacklist_characters=u'\\;:\"')


class TestFuzzing(unittest.TestCase):

    @given(lines=st.lists(
        st.tuples(key, st.dictionaries(key, value), value),
        min_size=1
    ))
    @settings(max_examples=10**9)
    def test_main(self, lines):
        cl = Contentlines()
        for key, params, value in lines:
            params = Parameters(**params)
            cl.append(Contentline.from_parts(key, params, value))
        cl.append('')

        assert Contentlines.from_ical(cl.to_ical()) == cl
