"""This tests the examples and their completeness."""

from pprint import pprint

import pytest


@pytest.mark.parametrize("index", [1, 2])
def test_example(index, calendars):
    """Check that the examples compy with jcal and ical parsing examples."""
    xcal = calendars[f"rfc_7265_appendix_example_{index}_xcal"]
    jcal = calendars[f"rfc_7265_appendix_example_{index}_jcal"]
    xcal2jcal = xcal.to_jcal()
    pprint(xcal2jcal)
    # compare with jcal - nicer pytest interface
    assert xcal2jcal == jcal.to_jcal()
