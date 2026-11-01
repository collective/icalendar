import pytest

from icalendar.parser import Parameters
from icalendar.prop import vCalAddress

txt = b"MAILTO:maxm@mxm.dk"
a = vCalAddress(txt)
a.params["cn"] = "Max M"


def test_to_ical():
    assert a.to_ical() == txt


def test_params():
    assert isinstance(a.params, Parameters)
    assert a.params == {"CN": "Max M"}


def test_from_ical():
    assert vCalAddress.from_ical(txt) == "MAILTO:maxm@mxm.dk"


def test_repr():
    instance = vCalAddress("value")
    assert repr(instance) == "vCalAddress('value')"


def test_email_malformed():
    """Sometimes, people forget to add mailto that."""
    address = vCalAddress("me@you.we")
    assert address.email == "me@you.we"


def test_email_mailto():
    """Email with a normal mailto link."""
    address = vCalAddress("mailto:icalendar@email.list")
    assert address.email == "icalendar@email.list"


def test_capital_email():
    """mailto can be capital letters."""
    address = vCalAddress("MAILTO:yemaya@posteo.net")
    assert address.email == "yemaya@posteo.net"


def test_name():
    """We want the name, too!"""
    address = vCalAddress("MAILTO:yemaya@posteo.net")
    assert address.name == ""
    address.params["CN"] = "name!"
    assert address.name == "name!"


def test_set_the_name():
    address = vCalAddress("MAILTO:yemaya@posteo.net")
    address.name = "Yemaya :)"
    assert address.name == "Yemaya :)"
    assert address.params["CN"] == "Yemaya :)"


@pytest.mark.parametrize(
    "value",
    [
        "mailto:icalendar@email.list",
        "MAILTO:yemaya@posteo.net",
        "me@you.we",
        "https://example.com/principals/jane",
    ],
)
def test_uri_is_the_unchanged_value(value):
    """The uri attribute returns the value as it is, like vUri.uri."""
    address = vCalAddress(value)
    assert address.uri == value
    assert type(address.uri) is str


def test_uri_is_the_same_as_ical_value():
    address = vCalAddress("mailto:icalendar@email.list")
    assert address.uri == address.ical_value
