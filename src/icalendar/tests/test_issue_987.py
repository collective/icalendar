"""This adds tests for refactoring."""

from datetime import timedelta

import pytest

from icalendar import vDDDLists, vRecur


def test_vdddtypes_cannot_be_hashed():
    """Mutable objects are not hashable."""
    with pytest.raises(TypeError):
        hash(vDDDLists([]))

    with pytest.raises(TypeError):
        hash(vDDDLists([timedelta(0)]))


def test_vrecur_cannot_be_hashed():
    """Mutable objects are not hashable."""
    with pytest.raises(TypeError):
        hash(vRecur([]))
