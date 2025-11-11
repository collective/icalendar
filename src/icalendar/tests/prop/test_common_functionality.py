"""Check some module consistency."""

import pytest

import icalendar
from icalendar import prop
from icalendar.tests.data import PARAMETER_NAMES


def test_all_propeties_are_exported(v_prop_name):
    """icalendar.prop should export all these properties."""
    assert v_prop_name in prop.__all__
    assert v_prop_name in icalendar.__all__
    assert getattr(prop, v_prop_name, None) is not None
    assert getattr(icalendar, v_prop_name, None) is not None


def test_all_properties_have_an_examples_method(v_prop):
    """All properties have a class method that returns a list of examples."""
    examples = v_prop.examples()
    assert isinstance(examples, list), "We expect a list of examples."
    assert len(examples) > 0, "We have examples."
    assert all(isinstance(example, v_prop) for example in examples), (
        "All examples should be of that type."
    )
    assert v_prop.__name__ in v_prop.examples.__doc__.splitlines()[0], (
        "type is in docstring"
    )


def test_all_properties_are_part_of_the_union_type(v_prop):
    """Check the union type captures all vProperty instances."""
    assert v_prop in prop.VPROPERTY.__args__


@pytest.mark.parametrize("no_prop", PARAMETER_NAMES)
def test_if_not_part_of_properties_they_are_not_included_in_the_type(no_prop):
    """If these are not properties rather parameters, do not include them."""
    assert no_prop not in prop.VPROPERTY.__args__


default_value_map = {
    prop.vBoolean: "BOOLEAN",
    prop.vCalAddress: "CAL-ADDRESS",
    prop.vCategory: "TEXT",
    prop.vDate: "DATE",
    prop.vDatetime: "DATETIME",
    prop.vDuration: "DURATION",
    prop.vFloat: "FLOAT",
    prop.vInt: "INT",
    prop.vPeriod: "PERIOD",
    prop.vRecur: "RECUR",
    prop.vText: "TEXT",
    prop.vTime: "TIME",
    prop.vUTCOffset: "UTC-OFFSET",
    prop.vUri: "URI",
    prop.vBinary: "BINARY",
    prop.vGeo: "GEO",
}


@pytest.mark.parametrize(("v_prop", "default_value"), list(default_value_map.items()))
def test_get_default_value(v_prop_example: prop.VPROPERTY, default_value: str):
    """Check the default value of all properties."""
    del v_prop_example.VALUE
    assert v_prop_example.VALUE == default_value
    assert "VALUE" not in v_prop_example.params


def test_set_value(v_prop_example):
    """Test setting the VALUE parameter."""
    v_prop_example.VALUE = "X-OTHER-VALUE"
    assert v_prop_example.VALUE == "X-OTHER-VALUE"
    assert v_prop_example.params.value == "X-OTHER-VALUE"


def test_delete_the_set_value(v_prop_example, v_prop):
    """The value is defaulting after delete."""
    v_prop_example.VALUE = "X-VALUE"
    del v_prop_example.VALUE
    assert v_prop_example.VALUE != "X-VALUE"
    if v_prop in default_value_map:
        assert v_prop_example.VALUE == default_value_map[v_prop], (
            "deleted value defaults"
        )


def test_value_of_datetime_list_and_type():
    pytest.skip("TODO")
