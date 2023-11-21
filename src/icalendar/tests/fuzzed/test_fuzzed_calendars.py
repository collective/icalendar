"""This test tests all fuzzed calendars."""
from icalendar.tests.fuzzed import fuzz_calendar_v1
import icalendar

def test_fuzz_v1(fuzz_v1_calendar):
    """Test a calendar."""
    with open(fuzz_v1_calendar, "rb") as f:
        fuzz_calendar_v1(
            icalendar.Calendar.from_ical,
            f.read(),
            multiple=True,
            should_walk=True
        )
