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


"""

import pytest

from icalendar.error import XCalParsingError
from icalendar.prop.recur import vRecur
from icalendar.tests.rfc_6321_xcal.common import list2xml

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
    assert recur["FREQ"] == freq


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
    ("bymonth", "12L", 12),
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
    assert result[key] == value


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
    assert result["foo"] == "bar"


@pytest.mark.parametrize("leap", [True, False])
def test_leap_month_from_xcal(leap):
    """The leap month has an L suffix."""
    xml = list2xml(["recur", ["bymonth", "12L" if leap else "12"]])
    result = vRecur.from_xcal(xml)
    assert result["bymonth"] == 12
    assert result["bymonth"].leap == leap


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
    # WKST
    # FREQ
    # SKIP
    # RSCALE
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
            f"Expected xsd:positiveInteger, got 'asd' in /recur/{key.lower()}[1].",
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
    assert result[key] == -1
    assert result[key].min == 0


def test_weekday_becomes_uppercase():
    """Uppercase is required for xCal."""
    xml = list2xml(["recur", ["byday", "su"]])
    result = vRecur.from_xcal(xml)
    assert result["BYDAY"] == "SU"
