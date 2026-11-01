from icalendar.prop import VPROPERTY
from icalendar.tests.rfc_6321_xcal.common import to_xcal, to_xcal_list


def test_parameters_are_the_first_element(xcal_prop_example: VPROPERTY):
    """The parameters always appear before the content."""
    xcal_prop_example.params["X-CUSTOM"] = "custom-value"
    xcal = to_xcal(xcal_prop_example)
    assert len(xcal) >= 1, (
        f"xCal: {xcal_prop_example.__class__.__name__} has no parameters."
    )
    parameters = xcal[0]
    assert parameters.tag == "parameters", (
        f"xCal: {xcal_prop_example.__class__.__name__} must put parameters first."
    )
    assert len(parameters) >= 1, (
        f"xCal: {xcal_prop_example.__class__.__name__} did not include the parameter values."
    )


def test_all_default_values_are_uppercase(v_prop):
    """The default_value property should be capital case always."""
    default_value = getattr(v_prop, "default_value", "")
    assert default_value.isupper(), (
        f"xCal: {v_prop.__name__} must have an uppercase default value."
    )


def test_parameters_are_collected_in_the_right_place(xcal_prop_example):
    """The parameters must be at the top in the parameters element."""
    xcal_prop_example.params.clear()
    xcal_prop_example.params["X-CUSTOM"] = "custom-value"
    xcal = to_xcal_list(xcal_prop_example, wrap=True)
    parameters = xcal[1]
    assert parameters[0] == "parameters"
    assert parameters[1][0] == "x-custom"
    # unknown is the right type, see https://datatracker.ietf.org/doc/html/rfc6321#section-5
    assert parameters[1][1] == ["unknown", "custom-value"]
