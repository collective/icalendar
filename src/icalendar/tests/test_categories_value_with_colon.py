"""A CATEGORIES value may contain an unescaped colon.

``TEXT`` values do not escape ``:``, so a category such as a URI is valid.
The value separator must be the first colon outside a quoted parameter
section, not the last colon on the line.
"""

from icalendar import Calendar
from icalendar.parser import Contentline


def _categories(value: str) -> list[str]:
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:1\r\n"
        f"CATEGORIES:{value}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    event = Calendar.from_ical(ics).walk("VEVENT")[0]
    return [str(c) for c in event["CATEGORIES"].cats]


def test_category_value_containing_a_colon_is_not_truncated():
    assert _categories("CONFIDENTIAL,http://example.com/tag") == [
        "CONFIDENTIAL",
        "http://example.com/tag",
    ]


def test_plain_categories_still_split_on_commas():
    assert _categories("HOME,WORK") == ["HOME", "WORK"]


def test_escaped_comma_in_category_is_preserved():
    assert _categories(r"Work,Personal\,Urgent") == ["Work", "Personal,Urgent"]


def test_colon_in_a_quoted_parameter_is_not_the_value_separator():
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "BEGIN:VEVENT\r\n"
        "UID:1\r\n"
        'CATEGORIES;ALTREP="http://p":A,B\r\n'
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
    event = Calendar.from_ical(ics).walk("VEVENT")[0]
    assert [str(c) for c in event["CATEGORIES"].cats] == ["A", "B"]
    assert event["CATEGORIES"].params["ALTREP"] == "http://p"


def test_value_separator_index_skips_quoted_colon():
    line = Contentline('CATEGORIES;ALTREP="http://p":A,B')
    assert line.value_separator_index() == line.index(":A,B")


def test_value_separator_index_does_not_treat_backslash_as_escape():
    # Backslash has no special meaning in the parameter grammar (RFC 5545
    # §3.1), so the first colon after ``X-A=\`` is the value separator and
    # the category is the single ``:``.
    line = Contentline(r"CATEGORIES;X-A=\::")
    assert line.value_separator_index() == 16
    assert str(line)[line.value_separator_index() + 1 :] == ":"
