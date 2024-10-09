"""Test the identity and equality between properties."""

from datetime import date, datetime, time

from icalendar import vDDDTypes
from icalendar.timezone.zoneinfo import zoneinfo

try:
    import pytz
except ImportError:
    pytz = None
from copy import deepcopy

import pytest
from dateutil import tz

vDDDTypes_list = [
    vDDDTypes(
        datetime(
            year=2022,
            month=7,
            day=22,
            hour=12,
            minute=7,
            tzinfo=zoneinfo.ZoneInfo("Europe/London"),
        )
    ),
    vDDDTypes(datetime(year=2022, month=7, day=22, hour=12, minute=7)),
    vDDDTypes(datetime(year=2022, month=7, day=22, hour=12, minute=7, tzinfo=tz.UTC)),
    vDDDTypes(date(year=2022, month=7, day=22)),
    vDDDTypes(date(year=2022, month=7, day=23)),
    vDDDTypes(time(hour=22, minute=7, second=2)),
]
if pytz:
    vDDDTypes_list.append(
        vDDDTypes(
            pytz.timezone("EST").localize(
                datetime(year=2022, month=7, day=22, hour=12, minute=7)
            )
        ),
    )


def identity(x):
    return x


@pytest.mark.parametrize(
    "map",
    [
        deepcopy,
        identity,
        hash,
    ],
)
@pytest.mark.parametrize("v_type", vDDDTypes_list)
@pytest.mark.parametrize("other", vDDDTypes_list)
def test_vDDDTypes_equivalance(map, v_type, other):
    if v_type is other:
        assert map(v_type) == map(other), f"identity implies equality: {map.__name__}()"
        assert map(v_type) == map(other), f"identity implies equality: {map.__name__}()"
    else:
        assert map(v_type) != map(other), f"expected inequality: {map.__name__}()"
        assert map(v_type) != map(other), f"expected inequality: {map.__name__}()"


@pytest.mark.parametrize("v_type", vDDDTypes_list)
def test_inequality_with_different_types(v_type):
    assert v_type != 42
    assert v_type != "test"
