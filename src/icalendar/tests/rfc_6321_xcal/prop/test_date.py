"""date converison

https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.4
"""

from datetime import date
from xml.etree import ElementTree as ET

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.dt import vDate, vDDDLists, vDDDTypes
from icalendar.prop.factory import TypesFactory


@pytest.fixture(params=[vDate, vDDDTypes, vDDDLists])
def v_date(request):
    """Fixture for vDate, vDDDTypes, and vDDDLists."""
    return request.param


mark_values = pytest.mark.parametrize(
    ("date", "xcal"),
    [
        (date(2011, 5, 17), "2011-05-17"),
        (date(2025, 11, 10), "2025-11-10"),
    ],
)


@mark_values
def test_to_xcal(v_date, date, xcal):
    """Convert to xcal."""
    e = v_date(date).to_xcal()
    assert isinstance(e, ET.Element)
    assert e.tag == "date"
    assert e.text == xcal
    assert ET.tostring(e, encoding="unicode") == f"<date>{xcal}</date>"


@mark_values
def test_from_xcal_from_factory(types_factory: TypesFactory, v_date, date, xcal):
    """Parse from xcal."""
    e = ET.Element("date")
    e.text = xcal
    result = types_factory.from_xcal("x-prop", e)
    assert result.dt == date


@mark_values
def test_from_xcal_from_dt_class(v_date, date, xcal):
    """Parse from xcal."""
    e = ET.Element("date")
    e.text = xcal
    result = v_date.from_xcal(e)
    assert result.dt == date


@pytest.mark.parametrize(
    ("xcal"),
    [
        "INVALID",
        "2025-1110",  # TODO: Be less strict
        "2025111",
        "202511100",
        "2025111A",
        None,
    ],
)
def test_invalid_value_from_xcal(v_date, xcal):
    """Parse from xcal with invalid value."""
    e = ET.Element("date")
    e.text = xcal
    with pytest.raises(XCalParsingError) as error:
        v_date.from_xcal(e)
    assert error.value.parser == vDate
    assert (
        error.value.message
        == f"Expected date format YYYY-MM-DD. Got {xcal!r} in 'date' element parsing 'vDate'."
    )
