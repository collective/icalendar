"""Check some module consistency."""

import pytest

import icalendar
from icalendar import prop

PROPERTY_NAMES = [attr for attr in dir(prop) if attr[0] == "v" and attr[1].isupper()]
PROPERTIES = [getattr(prop, name) for name in PROPERTY_NAMES]


@pytest.fixture(params=PROPERTY_NAMES)
def v_prop_name(request):
    """The name fxiture"""
    return request.param


@pytest.fixture
def v_prop(v_prop_name):
    """The name fxiture"""
    return getattr(prop, v_prop_name)


def test_all_propeties_are_exported(v_prop_name):
    """icalendar.prop should export all these properties."""
    assert v_prop_name in prop.__all__
    assert v_prop_name in icalendar.__all__
    assert getattr(prop, v_prop_name, None) is not None
    assert getattr(icalendar, v_prop_name, None) is not None


def test_all_properties_have_a_jcal_method(v_prop):
    """All properties should have a to_jcal() method."""
    assert hasattr(v_prop, "to_jcal")


def test_all_properties_have_an_examples_method(v_prop):
    """All properties have a class method that returns a list of examples."""
    examples = v_prop.examples()
    assert isinstance(examples, list), "We expect a list of examples."
    assert len(examples) > 0, "We have examples."
    assert all(isinstance(example, v_prop) for example in examples), (
        "All examples should be of that type."
    )


def test_all_properties_are_part_of_the_union_type(v_prop):
    """Check the union type captures all vProperty instances."""
    assert v_prop in prop.VPROPERTY.__args__
