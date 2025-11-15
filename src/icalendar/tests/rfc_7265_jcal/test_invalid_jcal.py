"""We would like to have certain errors for invalid JCal."""

from json import JSONDecodeError

import pytest

from icalendar import Component
from icalendar.error import JCalParsingError


@pytest.mark.parametrize("length", [0, 1, 2, 4, 5])
def test_component_is_too_short_or_too_long(length):
    """Test that a component has not enough values.

    See https://github.com/collective/icalendar/pull/979/#discussion_r2529703982

    """
    with pytest.raises(
        JCalParsingError, match="in Component: a component must be a list of 3 values"
    ):
        Component.from_jcal(["vevent", [], [], [], []][:length])


def test_invalid_json():
    """JSON can be invalid"""
    with pytest.raises(JSONDecodeError):
        Component.from_jcal("")


@pytest.fixture(params=[[], {}, None, 1, 1.3])
def str_expected(request):
    """Return everything else"""
    return request.param


@pytest.fixture(params=["a", {}, None, 1, 1.3])
def list_expected(request):
    """Return everything else"""
    return request.param


@pytest.fixture(params=["a", [], {}, None, 1, 1.3])
def object_expected(request):
    """Return everything else"""
    return request.param


@pytest.fixture(params=["a", [], {}, None, 1.3])
def int_expected(request):
    """Return everything else"""
    return request.param


@pytest.fixture(params=["a", [], {}, None, 1])
def float_expected(request):
    """Return everything else"""
    return request.param


def test_invalid_component_type(list_expected):
    """We expect a list for components."""
    if isinstance(list_expected, str):
        return  # skip JSON
    with pytest.raises(JCalParsingError, match="Component: a component must be a list"):
        Component.from_jcal(list_expected)
    with pytest.raises(
        JCalParsingError, match="\\[2\\]\\[0\\] in Calendar: a component must be a list"
    ):
        Component.from_jcal(["VCALENDAR", [], [list_expected]])


def test_invalid_component_name(str_expected):
    """Test the component name."""
    with pytest.raises(
        JCalParsingError, match="\\[0\\] in Component: name must be str"
    ):
        Component.from_jcal([str_expected, [], []])


def test_invalid_component_properties(list_expected):
    """Test the component properties."""
    with pytest.raises(
        JCalParsingError, match="\\[1\\] in Alarm: properties must be a list"
    ):
        Component.from_jcal(["valarm", list_expected, []])


def test_invalid_component_subcomponents(list_expected):
    """Test the component subcomponents."""
    with pytest.raises(
        JCalParsingError, match="\\[2\\] in Todo: subcomponents must be a list"
    ):
        Component.from_jcal(["vtodo", [], list_expected])


@pytest.mark.parametrize("i", [0, 3, 10])
def test_invalid_component_property(list_expected, i):
    """Test the component properties."""
    with pytest.raises(
        JCalParsingError, match=f"\\[1\\]\\[{i}\\] in Event: a property must be a list"
    ):
        Component.from_jcal(
            ["vevent", [["x-x", {}, "unknown", ""]] * i + [list_expected], []]
        )


# @pytest.mark.parametrize("length", [0, 1, 2, 3])
# def test_property_too_short(length, v_prop_example, v_prop):
#     """The example is too short."""
#     jcal = v_prop_example.to_jcal()
#     with pytest.raises(JCalParsingError, match="property: a property must be a list of at least 4 values."):
#         v_prop.from_jcal(jcal)

# @pytest.mark.parametrize("length", [0, 1, 2, 3])
# @pytest.mark.parametrize("index", [0, 3])
# def test_property_too_short_in_component(length, v_prop_example, v_prop, index):
#     """The example is too short."""
#     jcal = v_prop_example.to_jcal("X-PROP")
#     component = [
#         "vcalendar",
#         [jcal] * index + [jcal[:length]]
#     ]
#     with pytest.raises(JCalParsingError, match="[1][{index}] in property: a property must be a list of at least 4 values."):
#         Component.from_jcal(component)
