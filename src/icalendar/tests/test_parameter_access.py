"""Test the access to parameters via getter/setter properties."""

import pytest

from icalendar import Parameters
from icalendar.enums import VALUE


@pytest.fixture
def p():
    """Empty test property."""
    return Parameters()


def test_value_parameter_default(p):
    """Test default value."""
    assert p.value is None


def test_set_value(p):
    """Set the value, convert"""
    p.value = "test"
    assert p.value == "TEST"
    assert p["VALUE"] == "TEST"


def test_conversion(p):
    """Converted to enum."""
    p.value = "DATE-TIME"
    assert p.value == VALUE.DATE_TIME


def test_delete_value(p):
    """Delete the value."""
    p.value = "test"
    del p.value
    assert p.value is None
    assert "VALUE" not in p
    del p.value
    assert p.value is None
    assert "VALUE" not in p


def test_delete_value_None(p):
    """Delete the value."""
    p.value = "test"
    p.value = None
    assert p.value is None
    assert "VALUE" not in p
    p.value = None
    assert p.value is None
    assert "VALUE" not in p


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("base64", "BASE64"),
        ("BaSe64", "BASE64"),
        ("8bit", "8BIT"),
        (["base64", "8bit"], "8BIT"),
        (["8bit", "base64"], "BASE64"),
        ([], "8BIT"),
    ],
)
def test_encoding_parameter(value, expected):
    params = Parameters(encoding=value)
    assert params.encoding == expected
    assert params["ENCODING"] == value


def test_encoding_parameter_default_and_delete(p):
    assert p.encoding == "8BIT"
    assert "ENCODING" not in p
    p.encoding = "base64"
    assert p.encoding == "BASE64"
    assert p["ENCODING"] == "BASE64"
    del p.encoding
    assert p.encoding == "8BIT"
    assert "ENCODING" not in p
    p.encoding = "base64"
    p.encoding = None
    assert p.encoding == "8BIT"
    assert "ENCODING" not in p
    del p.encoding
    assert p.encoding == "8BIT"


@pytest.mark.parametrize(
    "value",
    ["ENCODING=8BIT;ENCODING=base64", "ENCODING=8BIT,base64"],
)
def test_repeated_encoding_parameter(value):
    assert Parameters.from_ical(value).encoding == "BASE64"
