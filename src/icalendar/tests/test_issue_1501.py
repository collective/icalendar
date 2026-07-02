"""Test the actual issue #1501 scenario - the round-trip a Google Calendar would see.

See https://github.com/collective/icalendar/issues/1501
A DESCRIPTION line that wraps at the column 75 boundary with a \n escape landing
at that fold produces an unfolded line where the escape sequence is broken across
two lines, which Google Calendar misinterprets and drops the event for.
"""
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from icalendar.prop import vText
from icalendar.parser import foldline

# Exact reproducer from the issue body.
DESCRIPTION = (
    "This is a description that will be wrapped, and it also has a\n"
    "new line in it right where it wraps. It does not display in Google"
)


def test_description_with_newline_at_fold_point():
    """The DESCRIPTION line must not fold across an escape sequence."""
    event = Event()
    event.add("summary", "Test event")
    event.add("uid", "123456789")
    event.add("dtstamp", datetime.now(timezone.utc))
    event.add("dtstart", datetime(2026, 7, 18))
    event.add("dtend", datetime(2026, 7, 20))
    event.add("location", vText("Place"))
    event.add("description", DESCRIPTION)
    rendered = event.to_ical().decode("utf-8")

    # The folded line must not contain a fold that lands between the
    # backslash and the escaped 'n' of an embedded newline. Specifically
    # the sequence "\r\n \\n" (CRLF + space + backslash + n) at the start
    # of a continuation line was the failing shape on the issue.
    assert "\r\n \\n" not in rendered, (
        "folding split an escape sequence across the fold: "
        f"\n{rendered}"
    )

    # Round-trip: re-parse the rendered ics and confirm the description
    # matches the original.
    cal = Calendar.from_ical(rendered)
    [parsed_event] = cal.walk("VEVENT")
    assert str(parsed_event["description"]) == DESCRIPTION


def test_foldline_keeps_escape_within_chunk():
    """foldline alone (without going through Calendar) must keep escapes together.

    The DESCRIPTION pre-rendering has already escaped the real newline to the
    literal two-character sequence ``\n`` (backslash + 'n').  foldline must
    never fold between those two characters, since doing so leaves a fold
    continuation line that starts with `n` (a continuation of the escape)
    and a parent line that ends with a stray backslash — see issue #1501.
    """
    from icalendar.parser.string import _escape_char
    line = (
        "DESCRIPTION:" + _escape_char(
            "This is a description that will be wrapped, and it also has a\n"
            "new line in it right where it wraps. It does not display in Google"
        )
    )
    assert "\n" not in line, f"input must be the escaped form: {line!r}"
    folded = foldline(line)
    # No continuation line may start with 'n' when the previous line ends
    # with a single backslash — that is the broken-escape shape on the
    # issue.
    chunks = folded.split("\r\n ")
    for i in range(1, len(chunks)):
        if chunks[i].startswith("n"):
            assert chunks[i - 1].endswith("\\"), (
                f"chunk {i} starts with 'n' but the previous chunk does "
                f"not end with a backslash — an escape was split: "
                f"{folded!r}"
            )
    # The escape sequence must still be present in the folded output.
    assert "\\n" in folded
    # Unfolding must restore the original line.
    assert folded.replace("\r\n ", "") == line


if __name__ == "__main__":
    test_description_with_newline_at_fold_point()
    test_foldline_keeps_escape_within_chunk()
    print("Both issue #1501 tests pass.")
