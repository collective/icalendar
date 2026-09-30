"""Test round tripping the properties and their parameters."""

from xml.etree.ElementTree import tostring

from icalendar.prop import VPROPERTY
from icalendar.tests.rfc_6321_xcal.common import to_xcal


def test_xcal_preserves_parameters(v_prop_example: VPROPERTY):
    """xcal serialization must include the parameters"""
    v_prop_example.params["X-CUSTOM"] = "custom-value"
    v_prop_example.params["TZID"] = "Europe/Paris"
    v_prop_example.params["RSVP"] = True
    v_prop_example.params["ALTREP"] = "https://other-location.com"
    xcal = to_xcal(v_prop_example)
    print("v_prop_example:", repr(v_prop_example))
    print("xcal:", tostring(xcal))
    v_prop = v_prop_example.__class__.from_xcal(xcal)
    print("v_prop:", repr(v_prop))
    assert v_prop.params.get("X-CUSTOM") == "custom-value", (
        f"custom-value missing in {v_prop}"
    )
    assert v_prop.params.get("TZID") == "Europe/Paris"
    assert v_prop.params.get("RSVP") == True  # noqa: E712
    assert v_prop.params.get("ALTREP") == "https://other-location.com"


def test_xcal_reproduces_the_example(v_prop_example: VPROPERTY):
    """xcal serialization must include the parameters"""
    xcal = to_xcal(v_prop_example, wrap=True)
    v_prop = v_prop_example.__class__.from_xcal(xcal)
    assert v_prop == v_prop_example
