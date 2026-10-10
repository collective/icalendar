import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from icalendar import Calendar, cli

INPUT = """
BEGIN:VCALENDAR
VERSION:2.0
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:Test Summary
ORGANIZER:organizer@test.test
ATTENDEE:attendee1@example.com
ATTENDEE:attendee2@test.test
COMMENT:Comment
DTSTART;TZID=Europe/Warsaw:20220820T103400
DTEND;TZID=Europe/Warsaw:20220820T113400
LOCATION:New Amsterdam, 1000 Sunrise Test Street
DESCRIPTION: Test Description
END:VEVENT
BEGIN:VEVENT
ORGANIZER:organizer@test.test
ATTENDEE:attendee1@example.com
SUMMARY:Test summary
DTSTART;TZID=Europe/Warsaw:20220820T200000
DTEND;TZID=Europe/Warsaw:20220820T203000
LOCATION:New Amsterdam, 1010 Test Street
DESCRIPTION:Test Description\\nThis one is multiline
END:VEVENT
BEGIN:VEVENT
UID:1
SUMMARY:TEST
DTSTART:20220511
DURATION:P5D
END:VEVENT
END:VCALENDAR
"""


def local_datetime(dt):
    return (
        datetime.strptime(dt, "%Y%m%dT%H%M%S")
        .replace(tzinfo=ZoneInfo("Europe/Warsaw"))
        .astimezone()
        .strftime("%c")
    )


# datetimes are displayed in the local timezone, so we cannot just hardcode them
firststart = local_datetime("20220820T103400")
firstend = local_datetime("20220820T113400")
secondstart = local_datetime("20220820T200000")
secondend = local_datetime("20220820T203000")

PROPER_OUTPUT = f"""    Organizer: organizer <organizer@test.test>
    Attendees:
     attendee1 <attendee1@example.com>
     attendee2 <attendee2@test.test>
    Summary    : Test Summary
    Starts     : {firststart}
    End        : {firstend}
    Duration   : 1:00:00
    Location   : New Amsterdam, 1000 Sunrise Test Street
    Comment    : Comment
    Description:
      Test Description

    Organizer: organizer <organizer@test.test>
    Attendees:
     attendee1 <attendee1@example.com>
    Summary    : Test summary
    Starts     : {secondstart}
    End        : {secondend}
    Duration   : 0:30:00
    Location   : New Amsterdam, 1010 Test Street
    Comment    : 
    Description:
     Test Description
     This one is multiline

    Organizer: 
    Attendees:

    Summary    : TEST
    Starts     : Wed May 11 00:00:00 2022
    End        : Mon May 16 00:00:00 2022
    Duration   : 5 days, 0:00:00
    Location   : 
    Comment    : 
    Description:
     

"""  # noqa: W291, W293


class CLIToolTest(unittest.TestCase):
    def test_output_is_proper(self):
        self.maxDiff = None
        calendar = Calendar.from_ical(INPUT)
        output = ""
        for event in calendar.walk("vevent"):
            output += cli.view(event) + "\n\n"
        assert output == PROPER_OUTPUT


class FormatNameTest(unittest.TestCase):
    """``_format_name`` must not invent an address pair without an email.

    A cal-address is a URI, so values such as ``urn:uuid:1234`` or a bare
    display name carry no ``@``. Splitting those on ``@`` produced a bogus
    ``1234 <1234>`` pair, and the empty-string guard could never fire because
    ``rsplit`` always leaves a non-empty tail.
    """

    def test_email_is_formatted(self):
        assert cli._format_name("mailto:bob@example.com") == "bob <bob@example.com>"

    def test_email_with_plus_and_subdomain(self):
        assert (
            cli._format_name("mailto:a.b+c@sub.example.co.uk")
            == "a.b+c <a.b+c@sub.example.co.uk>"
        )

    def test_uri_without_email_is_empty(self):
        assert cli._format_name("urn:uuid:1234") == ""

    def test_bare_display_name_is_empty(self):
        assert cli._format_name("Bob Smith") == ""

    def test_value_without_email_is_empty(self):
        assert cli._format_name("12345") == ""

    def test_mailto_without_recipient_is_empty(self):
        assert cli._format_name("mailto:bob") == ""

    def test_view_does_not_fabricate_an_organizer(self):
        # A join, not an f-string: the lines are data, not a format template.
        ics = "\r\n".join(  # noqa: FLY002
            [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//test//EN",
                "BEGIN:VEVENT",
                "UID:1",
                "SUMMARY:S",
                "ORGANIZER:urn:uuid:0e5f",
                "ATTENDEE:mailto:a@example.com",
                "DTSTART:20240101T090000Z",
                "END:VEVENT",
                "END:VCALENDAR",
                "",
            ]
        )
        event = Calendar.from_ical(ics).walk("vevent")[0]
        organizer = [
            line
            for line in cli.view(event).split("\n")
            if line.startswith("    Organizer:")
        ]
        assert organizer == ["    Organizer: "]


if __name__ == "__main__":
    unittest.main()
