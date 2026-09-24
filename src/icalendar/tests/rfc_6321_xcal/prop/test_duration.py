"""duration converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.4
"""

from datetime import timedelta
from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vDDDLists, vDDDTypes, vDuration
from icalendar.prop.factory import TypesFactory
from icalendar.tests.rfc_6321_xcal.common import to_xcal


@pytest.fixture(params=[vDuration, vDDDTypes, vDDDLists])
def v_duration(request):
    """Fixture for vDuration, vDDDTypes, and vDDDLists."""
    return request.param


mark_values = pytest.mark.parametrize(
    ("date", "xcal"),
    [
        (timedelta(days=15, hours=5, seconds=20), "P15DT5H0M20S"),
        (timedelta(days=49), "P49D"),
    ],
)


@mark_values
def test_to_xcal(v_duration, date, xcal):
    """Convert to xcal."""
    e = to_xcal(v_duration(date))
    assert isinstance(e, ET.Element)
    assert e.tag == "duration"
    assert e.text == xcal
    assert ET.tostring(e, encoding="unicode") == f"<duration>{xcal}</duration>"


@mark_values
def test_from_xcal_from_factory(types_factory: TypesFactory, v_duration, date, xcal):
    """Parse from xcal."""
    e = ET.Element("duration")
    e.text = xcal
    result = types_factory.from_xcal("x-prop", e)
    assert result.dt == date


@mark_values
def test_from_xcal_from_dt_class(v_duration, date, xcal):
    """Parse from xcal."""
    e = ET.Element("duration")
    e.text = xcal
    result = v_duration.from_xcal(e)
    assert result.dt == date


@pytest.mark.parametrize(
    ("xcal"),
    [
        "INVALID",
        None,
    ],
)
def test_invalid_value_from_xcal(v_duration, xcal):
    """Parse from xcal with invalid value."""
    e = ET.Element("duration")
    e.text = xcal
    with pytest.raises(XCalParsingError) as error:
        v_duration.from_xcal(e)
    assert error.value.parser == vDuration
    assert (
        error.value.message
        == f"Expected duration format https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.6. Got {xcal!r} in 'duration' element parsing 'vDuration'."
    )
