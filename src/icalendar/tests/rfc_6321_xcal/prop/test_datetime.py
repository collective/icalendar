"""date converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.4
"""

from datetime import UTC, datetime
from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vDatetime, vDDDLists, vDDDTypes
from icalendar.prop.factory import TypesFactory


@pytest.fixture(params=[vDatetime, vDDDTypes, vDDDLists])
def v_datetime(request):
    """Fixture for vDatetime, vDDDTypes, and vDDDLists."""
    return request.param


mark_values = pytest.mark.parametrize(
    ("date", "xcal"),
    [
        (datetime(2011, 5, 17, 20, 59), "2011-05-17T20:59:00"),
        (datetime(2025, 11, 10, 0, 0, 10, tzinfo=UTC), "2025-11-10T00:00:10Z"),
    ],
)


@mark_values
def test_to_xcal(v_datetime, date, xcal):
    """Convert to xcal."""
    e = v_datetime(date).to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "date-time"
    assert e.text == xcal
    assert ET.tostring(e, encoding="unicode") == f"<date-time>{xcal}</date-time>"


@mark_values
def test_from_xcal_from_factory(types_factory: TypesFactory, v_datetime, date, xcal):
    """Parse from xcal."""
    e = ET.Element("date-time")
    e.text = xcal
    result = types_factory.from_xcal("x-prop", e)
    assert result.dt == date


@mark_values
def test_from_xcal_from_dt_class(v_datetime, date, xcal):
    """Parse from xcal."""
    e = ET.Element("date-time")
    e.text = xcal
    result = v_datetime.from_xcal(e)
    assert result.dt == date


@pytest.mark.parametrize(
    ("xcal"),
    [
        "INVALID",
        "2025-1110",  # TODO: Be less strict if it is unambigious
        "2025111",
        "2025-11-10T00:0010",
        "2025111A",
        None,
    ],
)
def test_invalid_value_from_xcal(v_datetime, xcal):
    """Parse from xcal with invalid value."""
    e = ET.Element("date-time")
    e.text = xcal
    with pytest.raises(XCalParsingError) as error:
        v_datetime.from_xcal(e)
    assert error.value.parser == vDatetime
    assert (
        error.value.message
        == f"Expected date-time format YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SSZ. Got {xcal!r} in 'date-time' element parsing 'vDatetime'."
    )
