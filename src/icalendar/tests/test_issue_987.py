"""This adds tests for refactoring."""

from datetime import timedelta

import pytest

from icalendar import vDDDLists


def test_vdddtypes_cannot_be_hashed():
    with pytest.raises(TypeError):
        hash(vDDDLists([]))

    with pytest.raises(TypeError):
        hash(vDDDLists([timedelta(0)]))
