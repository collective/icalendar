r"""``URI``, ``CAL-ADDRESS`` and inline values must reject raw CR and LF.

Unlike ``TEXT``, these value types are not escaped on serialization, so a raw
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

VERBATIM_VALUE_TYPES = [vUri, vCalAddress, vInline, vXmlReference]

CRLF_INJECTION_VALUES = [
    "mailto:a@b.com\rINJECTED:evil",
    "mailto:a@b.com\nINJECTED:evil",
    "http://e.com/a\r\nX-EVIL:1",
    "trailing\r",
]

JCAL_PROPERTIES = [
    ("url", "uri"),
    ("attendee", "cal-address"),
    ("organizer", "cal-address"),
]


@pytest.mark.parametrize("cls", VERBATIM_VALUE_TYPES)
@pytest.mark.parametrize("value", CRLF_INJECTION_VALUES)
def test_value_rejects_cr_and_lf(cls, value):
    with pytest.raises(ValueError):
        cls.from_ical(value)


@pytest.mark.parametrize("cls", VERBATIM_VALUE_TYPES)
def test_valid_values_still_parse(cls):
    assert cls.from_ical("http://example.com/my-report.txt")


@pytest.mark.parametrize(("prop", "jcal_type"), JCAL_PROPERTIES)
@pytest.mark.parametrize("value", CRLF_INJECTION_VALUES)
def test_jcal_value_with_cr_or_lf_is_rejected(prop, jcal_type, value):
    """A CR or LF from untrusted jCal must not reach the serialized output."""
    jcal = [
        "vcalendar",
        [["version", {}, "text", "2.0"], ["prodid", {}, "text", "x"]],
        [
            [
                "vevent",
                [
                    ["uid", {}, "text", "1"],
                    [prop, {}, jcal_type, value],
                ],
                [],
            ]
        ],
    ]
    with pytest.raises(ValueError):
        Calendar.from_jcal(jcal)
