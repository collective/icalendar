"""Test RECUR xCal conversion.


Recur is influenced by these standards:
- :rfc:`5545` - the base
- :rfc:`7529` - SKIP parameter and leap month, RSCALE

Example:

.. code-block:: xml

    <recur>
        <freq>YEARLY</freq>
        <count>5</count>
        <byday>-1SU</byday>
        <bymonth>10</bymonth>
    </recur>

Notes on UNITL:
https://errata.rfc-editor.org/eid3315/
This is not clearly defined. We will parse both here.
When we serialize, we put the tag around it.
It is common practice in xCal that the tag determines the pattern.
Submitted a suggestion:
https://errata.rfc-editor.org/new/preview/d637989c-0123-4b09-ab79-b1c78f183ed2/

"""

from datetime import date, datetime, timezone
from pprint import pprint

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.recur import vRecur
from icalendar.prop.recur.month import vMonth
from icalendar.tests.rfc_6321_xcal.common import list2xml, to_xcal_list

VALID_FREQ = ["SECONDLY", "MINUTELY", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "YEARLY"]


@pytest.fixture(params=VALID_FREQ)
def freq(request):
    return request.param


def test_from_xcal_freq_is_not_required_for_parsing():
    """When parsing, we do not require a <freq>.

    Design decision: This is an invalid calendar but we can parse it, so we do.
    We do not raise InvalidCalendar, only XCalParsingError.
    """
    xml = list2xml(["recur", ["count", "5"]])
    recur = vRecur.from_xcal(xml)
    assert "FREQ" not in recur


@pytest.mark.parametrize("freq", VALID_FREQ)
def test_from_xcal_freq(freq):
    """Test that the valid values can be parsed."""
    xml = list2xml(["recur", ["freq", freq], ["count", "5"]])
    recur = vRecur.from_xcal(xml)
    assert recur["FREQ"] == [freq]


# These values appear at most once
SINGLE_VALUE = [
    # FREQ
    ("freq", "YEARLY", "YEARLY"),
    ("freq", "SECONDLY", "SECONDLY"),
    # COUNT
    ("count", "100", 100),
    ("count", "4", 4),
    # INTERVAL
    ("interval", "2", 2),
    ("interval", "13", 13),
    # WKST
    ("wkst", "SU", "SU"),
    ("wkst", "MO", "MO"),
    # SKIP
    ("skip", "OMIT", "OMIT"),
    ("skip", "FORWARD", "FORWARD"),
    # RSCALE
    ("rscale", "GREGORIAN", "GREGORIAN"),
    ("rscale", "HEBREW", "HEBREW"),
    # UNTIL
    # These are text values. We still parse them.
    (
        "until",
        "2014-01-01T00:02:03Z",
        datetime(2014, 1, 1, 0, 2, 3, tzinfo=timezone.utc),
    ),
    ("until", "2014-01-01T00:02:03", datetime(2014, 1, 1, 0, 2, 3)),
    ("until", "2014-03-04", date(2014, 3, 4)),
]

# These values can appear several times.
MULTI_VALUE = [
    # BYSECOND
    ("bysecond", "10", 10),
    ("bysecond", "59", 59),
    # BYMINUTE
    ("byminute", "10", 10),
    ("byminute", "59", 59),
    # BYHOUR
    ("byhour", "10", 10),
    ("byhour", "23", 23),
    # BYMONTH
    ("bymonth", "1", 1),
    ("bymonth", "12L", vMonth("12L")),
    # BYWEEKNO
    ("byweekno", "10", 10),
    ("byweekno", "32", 32),
    # BYMONTHDAY
    ("bymonthday", "1", 1),
    ("bymonthday", "12", 12),
    # BYYEARDAY
    ("byyearday", "10", 10),
    ("byyearday", "-340", -340),
    # BYSETPOS
    ("bysetpos", "10", 10),
    ("bysetpos", "300", 300),
    # BYDAY
    ("byday", "2TH", "2TH"),
    ("byday", "FR", "FR"),
    ("byday", "-1SU", "-1SU"),
    # BYWEEKDAY does not exist
    # see https://github.com/collective/icalendar/issues/1854
]

mark_single_value = pytest.mark.parametrize(
    ("key", "xml", "value"), SINGLE_VALUE + MULTI_VALUE
)


@mark_single_value
def test_from_xcal(key, xml, value):
    """Parse from xcal."""
    xml = list2xml(["recur", [key, xml]])
    result = vRecur.from_xcal(xml)
    assert isinstance(result, vRecur)
    assert result[key] == [value]


MULTI_VALUE_COMBINATION = [
    (m1[0], m1[1], m1[2], m2[1], m2[2])
    for m1 in MULTI_VALUE
    for m2 in MULTI_VALUE
    if m1[0] == m2[0] and m1 != m2
]

mark_multi_value = pytest.mark.parametrize(
    ("key", "xml1", "value1", "xml2", "value2"), MULTI_VALUE_COMBINATION
)


@mark_multi_value
def test_from_xcal_multi(key, xml1, value1, xml2, value2):
    """Multiple values get put into a list."""
    xml = list2xml(["recur", [key, xml1], [key, xml2]])
    result = vRecur.from_xcal(xml)
    assert isinstance(result, vRecur)
    assert result[key] == [value1, value2]


def test_from_xcal_if_key_is_not_present_it_does_not_appear():
    """Only present keys should be there."""
    xml = list2xml(["recur", ""])
    result = vRecur.from_xcal(xml)
    assert len(result) == 0


def test_unknown_parameters_are_also_included():
    """New RFCs might extend the parameters. We include them."""
    xml = list2xml(["recur", ["foo", "bar"]])
    result = vRecur.from_xcal(xml)
    assert result["foo"] == ["bar"]


@pytest.mark.parametrize("leap", [True, False])
def test_leap_month_from_xcal(leap):
    """The leap month has an L suffix."""
    xml = list2xml(["recur", ["bymonth", "12L" if leap else "12"]])
    result = vRecur.from_xcal(xml)
    assert result["bymonth"] == [12]
    assert result["bymonth"][0].leap == leap


INVALID_VALUE = [
    # BYMONTH
    (
        "bymonth",
        "asd",
        "Expected month number, got 'asd' in /recur/bymonth[1].",
    ),
    # BYDAY
    (
        "byday",
        "asd",
        "Expected weekday https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10, got 'asd' in /recur/byday[1].",
    ),
    # UNTIL
    (
        "until",
        "asd",
        "Expected date format YYYY-MM-DD, got 'asd' in /recur/until[1].",
    ),
    # WKST
    (
        "wkst",
        "asd",
        "Expected weekday https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10, got 'asd' in /recur/wkst[1].",
    ),
    # FREQ
    (
        "freq",
        "asd",
        "Expected frequency https://datatracker.ietf.org/doc/html/rfc5545#section-3.3.10, got 'asd' in /recur/freq[1].",
    ),
    # SKIP
    (
        "skip",
        "asd",
        "Expected OMIT|BACKWARD|FORWARD https://datatracker.ietf.org/doc/html/rfc7529#section-4.1, got 'asd' in /recur/skip[1].",
    ),
    # RSCALE
    # For RSCALE, we use text, so there is no issue.
]

POSITIVE_INTS = [
    "COUNT",
    "INTERVAL",
    "BYSECOND",
    "BYMINUTE",
    "BYHOUR",
    # BYMONTH is handeled by vMonth in extra tests.
]

for key in POSITIVE_INTS:
    INVALID_VALUE.append(
        (
            key,
            "asd",
            f"Expected xsd:nonNegativeInteger, got 'asd' in /recur/{key.lower()}[1].",
        )
    )

INTS = ["BYWEEKNO", "BYMONTHDAY", "BYYEARDAY", "BYSETPOS"]

for key in INTS:
    INVALID_VALUE.append(
        (key, "asd", f"Expected xsd:integer, got 'asd' in /recur/{key.lower()}[1].")
    )


@pytest.mark.parametrize(("key", "xml", "message"), INVALID_VALUE)
def test_invalid_values_raise_xcal_error(key, xml, message):
    """These invalid values raise an XCalParsingError.

    Sometimes, we might be forgiving. But during parsing,
    this is the only error allowed.
    """
    xml = list2xml(["recur", [key, xml]])
    with pytest.raises(XCalParsingError) as e:
        vRecur.from_xcal(xml)
    assert e.value.message == message


@pytest.mark.parametrize("key", POSITIVE_INTS)
def test_negative_integer_still_parses(key):
    """We still want to preserve invalid values because
    - we might just want to convert a calendar
    - we might not be interested in them
    """
    xml = list2xml(["recur", [key, "-1"]])
    result = vRecur.from_xcal(xml)
    assert result[key] == [-1]
    assert result[key][0].min == 0


def test_weekday_becomes_uppercase():
    """Uppercase is required for xCal."""
    xml = list2xml(["recur", ["byday", "su"]])
    result = vRecur.from_xcal(xml)
    assert result["BYDAY"] == ["SU"]


@pytest.mark.parametrize(
    ("xml", "expected"),
    [
        (["date", "2021-01-01"], date(2021, 1, 1)),
        (["date-time", "1998-12-23T11:45:00"], datetime(1998, 12, 23, 11, 45)),
        (
            ["date-time", "1998-12-23T11:45:01Z"],
            datetime(1998, 12, 23, 11, 45, 1, tzinfo=timezone.utc),
        ),
    ],
)
def test_until_with_tags(xml, expected):
    """Test the UNTIL date value."""
    xml = list2xml(["recur", ["until", xml]])
    result = vRecur.from_xcal(xml)
    assert result["UNTIL"] == [expected]


@mark_single_value
def test_to_xcal_init(key, xml, value):
    """Parse from xcal."""
    recur = vRecur(**{key: value})
    assert_xcal_matches(recur, [key, xml])


@mark_single_value
def test_to_xcal_setter(key, xml, value):
    """Parse from xcal."""
    recur = vRecur()
    recur[key] = value
    assert_xcal_matches(recur, [key, xml])


def assert_xcal_matches(recur: vRecur, *values: list[str]):
    expected = ["TEST", ["recur"] + list(values)]
    result = to_xcal_list(recur)
    pprint(expected)
    pprint(result)
    assert result == expected


@mark_multi_value
def test_to_xcal_init_multi(key, xml1, value1, xml2, value2):
    """Parse from xcal."""
    recur = vRecur(**{key: [value1, value2]})
    assert_xcal_matches(recur, [key, xml1], [key, xml2])


@mark_multi_value
def test_to_xcal_setter_multi(key, xml1, value1, xml2, value2):
    """Parse from xcal."""
    recur = vRecur()
    recur[key] = [value1, value2]
    assert_xcal_matches(recur, [key, xml1], [key, xml2])


RECUR_VALUES = list(
    {key: value for key, _xml, value in SINGLE_VALUE + MULTI_VALUE}.items()
)
RECUR_VALUES.sort()  # differen order

ORDER = [key for key in vRecur.canonical_order if key != "BYWEEKDAY"]


def test_canonical_order():
    """The order of keys does not matter. It is always the same."""
    recur1 = vRecur()
    recur2 = vRecur()
    for key, value in RECUR_VALUES:
        recur1[key] = value
    for key, value in reversed(RECUR_VALUES):
        recur2[key] = value
        assert key.upper() in ORDER, "All test keys are ordered"
    for key in ORDER:
        assert key in recur1, f"All canonical keys are in the test data: {key}"
        assert key in recur2, f"All canonical keys are in the test data: {key}"
    xml1 = to_xcal_list(recur1)
    xml2 = to_xcal_list(recur2)
    keys = [val[0].upper() for val in xml1[1][1:]]
    assert keys == ORDER
    pprint(xml1)
    pprint(xml2)
    assert xml1 == xml2
