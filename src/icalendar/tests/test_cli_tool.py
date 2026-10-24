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

    def test_control_characters_are_escaped(self):
        calendar = Calendar.from_ical(
            "BEGIN:VEVENT\r\n"
            "ORGANIZER:mailto:boss\x1b]0;title\x07@example.com\r\n"
            "ATTENDEE:mailto:a\x1b[2K@example.com\r\n"
            "SUMMARY:Lunch\u009b2K\r\n"
            "DTSTART:20220511\r\n"
            "END:VEVENT\r\n"
        )
        output = cli.view(calendar)
        assert "\x1b" not in output
        assert "\x07" not in output
        assert "\x9b" not in output
        assert "boss\\x1b]0;title\\x07@example.com" in output
        assert "a\\x1b[2K@example.com" in output
        assert "Lunch\\x9b2K" in output


if __name__ == "__main__":
    unittest.main()
