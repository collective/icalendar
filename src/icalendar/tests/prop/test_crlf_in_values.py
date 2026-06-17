r"""``URI``, ``CAL-ADDRESS`` and inline values must reject raw CR and LF.

Unlike ``TEXT`` these value types are not escaped on serialisation, so a raw
``\r`` or ``\n`` in the value is written straight into the content line. A lone
``\r`` slips past the newline-only assertion in ``Contentline`` and reparses as
a separate property for consumers that treat a bare CR as a line break, which
is content-line injection. The values now reject CR and LF at construction.
"""

import pytest

from icalendar import Calendar, vCalAddress
from icalendar.prop import vUri
from icalendar.prop.inline import vInline
from icalendar.prop.xml_reference import vXmlReference


@pytest.mark.parametrize("cls", [vUri, vCalAddress, vInline, vXmlReference])
@pytest.mark.parametrize(
    "value",
    [
        "mailto:a@b.com\rINJECTED:evil",
        "mailto:a@b.com\nINJECTED:evil",
        "http://e.com/a\r\nX-EVIL:1",
        "trailing\r",
    ],
)
def test_value_rejects_cr_and_lf(cls, value):
    with pytest.raises(ValueError):
        cls.from_ical(value)


@pytest.mark.parametrize("cls", [vUri, vCalAddress, vInline, vXmlReference])
def test_valid_values_still_parse(cls):
    assert cls.from_ical("http://example.com/my-report.txt")


def test_jcal_uri_value_with_cr_is_rejected():
    """A lone CR from untrusted jCal must not reach the serialised output."""
    jcal = [
        "vcalendar",
        [["version", {}, "text", "2.0"], ["prodid", {}, "text", "x"]],
        [
            [
                "vevent",
                [
                    ["uid", {}, "text", "1"],
                    ["url", {}, "uri", "http://e.com/a\rX-EVIL:1"],
                ],
                [],
            ]
        ],
    ]
    with pytest.raises(ValueError):
        Calendar.from_jcal(jcal)
