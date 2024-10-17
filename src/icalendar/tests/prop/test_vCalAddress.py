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
