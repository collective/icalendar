import pytest
import unittest

from datetime import datetime
import os
import icalendar

def test_recurrence_properly_parsed(events):
    assert events.event_with_recurrence['rrule'] == {'COUNT': [100], 'FREQ': ['DAILY']}

@pytest.mark.parametrize('i, exception_date', [
    (0, datetime(1996, 4, 2, 1, 0)),
    (1, datetime(1996, 4, 3, 1, 0)),
    (2, datetime(1996, 4, 4, 1, 0))
])
def test_exdate_properly_parsed(events, i, exception_date, in_timezone):
    assert events.event_with_recurrence['exdate'].dts[i].dt == in_timezone(exception_date, 'UTC')

def test_exdate_properly_marshalled(events):
    actual = events.event_with_recurrence['exdate'].to_ical()
    assert actual == b'19960402T010000Z,19960403T010000Z,19960404T010000Z'

class TestRecurrence(unittest.TestCase):

    def setUp(self):
        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'recurrence.ics'), 'rb') as fp:
            data = fp.read()
        self.cal = icalendar.Calendar.from_ical(data)

    def test_recurrence_exdates_multiple_lines(self):
        event = self.cal.walk('vevent')[1]

        exdate = event['exdate']

        # TODO: DOCUMENT BETTER!
        # In this case we have multiple EXDATE definitions, one per line.
        # Icalendar makes a list out of this instead of zipping it into one
        # vDDDLists object. Actually, this feels correct for me, as it also
        # allows to define different timezones per exdate line - but client
        # code has to handle this as list and not blindly expecting to be able
        # to call event['EXDATE'].to_ical() on it:
        self.assertEqual(isinstance(exdate, list), True)  # multiple EXDATE
        self.assertEqual(exdate[0].to_ical(), b'20120529T100000')

        # TODO: test for embedded timezone information!
