"""Tests for the vGeo property type."""

import pytest

from icalendar.prop.geo import vGeo


def test_to_ical_returns_bytes():
    """vGeo.to_ical() must return bytes, not str, to match every other vDataType.

    Every other vDataType's to_ical() (vFloat, vInt, vText, vBoolean, vUri,
    vBinary, vDate, vDatetime, vDuration, vPeriod, vRecur, vTime,
    vUTCOffset) returns bytes.  vGeo was the lone str-returning outlier,
    which broke callers that concatenated `b"\\r\\n".join(x.to_ical() for x in lines)`
    (e.g. Contentlines.to_ical in parser/content_line.py) once any property
    held a vGeo.
    """
    assert isinstance(vGeo((37.386013, -122.082932)).to_ical(), bytes)


def test_to_ical_value_bytes():
    """vGeo.to_ical() returns the encoded lat;lon string."""
    assert vGeo((37.386013, -122.082932)).to_ical() == b"37.386013;-122.082932"


def test_to_ical_list_and_tuple_both_bytes():
    """Both list and tuple inputs produce the same bytes output."""
    assert vGeo([1.2, 3.0]).to_ical() == b"1.2;3.0"
    assert vGeo((1.2, 3.0)).to_ical() == b"1.2;3.0"


def test_from_ical_roundtrip():
    """from_ical -> vGeo -> to_ical roundtrips back to the original bytes."""
    original = "37.386013;-122.082932"
    parsed = vGeo.from_ical(original)
    assert vGeo(parsed).to_ical() == original.encode()


def test_negative_coordinates_bytes():
    """Negative latitude or longitude serialises to bytes with the minus sign."""
    assert vGeo((-37.5, 122.0)).to_ical() == b"-37.5;122.0"


def test_integer_inputs_serialise_as_floats():
    """Integer latitude/longitude inputs serialise with a decimal point.

    Without a decimal, the output would be ``b"37;-122"``, which `from_ical`
    still parses correctly but is inconsistent with the float format
    documented in RFC 5545 (``(["+"] / "-") 1*DIGIT ["." 1*DIGIT]`` is
    recommended).
    """
    result = vGeo((37, -122)).to_ical()
    assert result == b"37.0;-122.0"
    assert isinstance(result, bytes)
