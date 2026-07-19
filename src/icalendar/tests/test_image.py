"""Test the image class to convert from and to binary data."""

from __future__ import annotations

import base64

import pytest

from icalendar import Calendar, Component, Image, vBinary, vUnknown, vUri
from icalendar.prop import TypesFactory, vText

TRANSPARENT_PIXEL = base64.b64decode("""iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCA
YAAAAfFcSJAAAACXBIWXMAAAAnAAAAJwEqCZFPAAAAGXRFWHRTb2Z0d2FyZQB3d3cuaW5rc2NhcGUub3Jn
m+48GgAAAA1JREFUCJlj+P//PwMACPwC/oXNqzQAAAAASUVORK5CYII=""")


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [
        ("URI", vUri),
        ("BINARY", vBinary),
        (None, vUnknown),
        ("TEXT", vUnknown),
    ],
)
def test_image_value_type(value, expected_type):
    """IMAGE uses explicit RFC 7986 value types and otherwise stays unknown."""
    assert TypesFactory().for_property("IMAGE", value) is expected_type


def test_image_binary_round_trip_preserves_bytes():
    """IMAGE binary data is not corrupted while parsing and serializing."""
    data = bytes(range(256))
    encoded = base64.b64encode(data).decode("ascii")
    ics = (
        "BEGIN:VEVENT\r\n"
        "UID:1\r\n"
        f"IMAGE;ENCODING=BASE64;VALUE=BINARY:{encoded}\r\n"
        "END:VEVENT\r\n"
    )

    event = Component.from_ical(ics)
    image = event["IMAGE"]

    assert isinstance(image, vBinary)
    assert image.ical_value == data
    reparsed = Component.from_ical(event.to_ical())
    assert isinstance(reparsed["IMAGE"], vBinary)
    assert reparsed["IMAGE"].ical_value == data


def test_image_uri_and_unknown_values():
    """IMAGE only defaults to unknown when VALUE is omitted."""
    event = Component.from_ical(
        "BEGIN:VEVENT\r\n"
        "UID:1\r\n"
        "IMAGE;VALUE=URI:https://example.com/a.png\r\n"
        "IMAGE:https://example.com/b.png\r\n"
        "END:VEVENT\r\n"
    )

    uri, unknown = event["IMAGE"]
    assert isinstance(uri, vUri)
    assert isinstance(unknown, vUnknown)


@pytest.fixture
def images(calendars) -> dict[str, Image]:
    """Return the images we get from the example calendars."""
    calendar: Calendar = calendars.rfc_7986_image
    images: dict[str, Image] = {}
    for component in calendar.subcomponents:
        img = component.images[0]
        images[component.uid] = img
    return images


@pytest.mark.parametrize(
    ("uid", "uri", "data", "fmt_type", "altrep", "display"),
    [
        (
            "uri-event",
            "http://example.com/images/party.png",
            None,
            "image/png",
            None,
            "BADGE",
        ),
        (
            "uri-todo",
            "http://example.com/images/party.jpg",
            None,
            None,
            None,
            "BADGE",
        ),
        (
            "uri-journal",
            "http://example.com/images/party.jpg",
            None,
            "image/jpg",
            None,
            "ICON",
        ),
        (
            "data-event",
            None,
            TRANSPARENT_PIXEL,
            "image/png",
            None,
            None,
        ),
        (
            "data-todo",
            None,
            TRANSPARENT_PIXEL,
            "image/png",
            "http://example.com/images/party.jpg",
            None,
        ),
        (
            "data-journal",
            None,
            TRANSPARENT_PIXEL,
            "image/png",
            None,
            "BADGE",
        ),
    ],
)
def test_image_parsing(
    images,
    uid,
    uri,
    data,
    fmt_type,
    altrep,
    display,
):
    """Test that the image property is parsed correctly."""
    image = images[uid]
    assert image.uri == uri
    assert image.data == data
    assert image.fmttype == fmt_type
    assert image.altrep == altrep
    assert image.display == display


def test_no_images():
    """Test that an empty calendar has no images."""
    calendar = Calendar()
    assert len(calendar.images) == 0


def test_create_image_invalid_type():
    """Test that creating an image with invalid type raises TypeError."""
    with pytest.raises(TypeError):
        Image.from_property_value("not a valid type")
    with pytest.raises(TypeError):
        Image.from_property_value(vText("not a valid type", params={"VALUE": "TEXT"}))
    with pytest.raises(TypeError):
        Image.from_property_value(vText("http://example.com/image.png"))


def test_create_image_invalid_params():
    """Test that creating an image with invalid params raises TypeError."""

    class DummyValue:
        params = "invalid"

    with pytest.raises(TypeError):
        Image.from_property_value(DummyValue())


def test_create_with_vBinary():
    """Test creating an Image from a vBinary property."""
    b64data = base64.b64encode(TRANSPARENT_PIXEL).decode("ascii")
    vbin = vBinary(b"", params={"FMTTYPE": "image/png"})
    vbin.base64data = b64data
    image = Image.from_property_value(vbin)
    assert image.uri is None
    assert image.data == TRANSPARENT_PIXEL
    assert image.fmttype == "image/png"
    assert image.altrep is None
    assert image.display is None


def test_create_with_vUri():
    """Test creating an Image from a vUri property."""
    uri = "http://example.com/image.png"
    vuri = vUri(uri, params={"FMTTYPE": "image/png", "DISPLAY": "BADGE"})
    image = Image.from_property_value(vuri)
    assert image.uri == uri
    assert image.data is None
    assert image.fmttype == "image/png"
    assert image.altrep is None
    assert image.display == "BADGE"


def test_create_image_with_vText_as_uri():
    """Test that creating an image with vText but VALUE URI or BINARY raises TypeError."""
    img = Image.from_property_value(
        vText("http://example.com/image.png", params={"VALUE": "URI"})
    )
    assert img.uri == "http://example.com/image.png"
    assert img.data is None
    assert img.fmttype is None
    assert img.altrep is None
    assert img.display is None


def test_create_image_with_vText_as_binary():
    """Test that creating an image with vText but VALUE URI or BINARY raises TypeError."""
    b64data = base64.b64encode(TRANSPARENT_PIXEL).decode("ascii")
    img = Image.from_property_value(vText(b64data, params={"VALUE": "BINARY"}))
    assert img.uri is None
    assert img.data == TRANSPARENT_PIXEL
    assert img.fmttype is None
    assert img.altrep is None
    assert img.display is None


def test_requires_uri_xor_binary():
    """Test forbidden parameter combinations."""
    with pytest.raises(ValueError):
        Image()
    with pytest.raises(ValueError):
        Image(b64data="", uri="http://example.com/image.png")
