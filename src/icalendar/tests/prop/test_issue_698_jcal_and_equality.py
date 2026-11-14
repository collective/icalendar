"""Cover equality and jCal dispatch branches of property types.

See https://github.com/PyCalendar/icalendar/issues/698
"""

from datetime import timedelta

import pytest

from icalendar.error import JCalParsingError
from icalendar.prop import (
    vCategory,
    vFloat,
    vGeo,
    vRequestStatus,
    vText,
    vUnknown,
    vUTCOffset,
)


def test_vutcoffset_is_not_equal_to_other_types():
    assert vUTCOffset(timedelta(hours=2)) != "+0200"


def test_equal_vutcoffsets_have_equal_hashes():
    offset = vUTCOffset(timedelta(hours=-5, minutes=-30))
    assert hash(offset) == hash(vUTCOffset(timedelta(hours=-5, minutes=-30)))
    assert len({offset, vUTCOffset(timedelta(hours=-5, minutes=-30))}) == 1


def test_vcategory_comparison_with_other_types_is_not_implemented():
    category = vCategory(["WORK"])
    assert category.__eq__(1) is NotImplemented
    assert category != 1


def test_vfloat_from_jcal_delegates_geo_to_vgeo():
    geo = vFloat.from_jcal(["geo", {}, "float", [37.386013, -122.082932]])
    assert isinstance(geo, vGeo)
    assert (geo.latitude, geo.longitude) == (37.386013, -122.082932)


def test_vtext_from_jcal_delegates_request_status_to_vrequeststatus():
    status = vText.from_jcal(["request-status", {}, "text", ["2.0", "Success"]])
    assert isinstance(status, vRequestStatus)
    assert status.code == (2, 0)
    assert status.description == "Success"


@pytest.mark.parametrize(
    ("value", "expected"), [("text", "text"), (42, "42"), (1.5, "1.5")]
)
def test_vunknown_parse_jcal_value_accepts_scalars(value, expected):
    assert vUnknown.parse_jcal_value(value) == vUnknown(expected)


def test_vunknown_parse_jcal_value_rejects_lists():
    with pytest.raises(JCalParsingError, match="must be a string or an integer"):
        vUnknown.parse_jcal_value(["text"])
