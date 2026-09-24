from icalendar.prop import VPROPERTY
from icalendar.tests.rfc_6321_xcal.common import to_xcal


def test_parameters_are_the_first_element(v_prop_example: VPROPERTY):
    """The parameters always appear before the content."""
    v_prop_example.params["X-CUSTOM"] = "custom-value"
    xcal = to_xcal(v_prop_example)
    assert len(xcal) >= 1, (
        f"xCal: {v_prop_example.__class__.__name__} has no parameters."
    )
    parameters = xcal[0]
    assert parameters.tag == "parameters", (
        f"xCal: {v_prop_example.__class__.__name__} must put parameters first."
    )
    assert len(parameters) >= 1, (
        f"xCal: {v_prop_example.__class__.__name__} did not include the parameter values."
    )
