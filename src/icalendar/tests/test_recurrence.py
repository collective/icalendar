from datetime import datetime

import pytest

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

# TODO: DOCUMENT BETTER!
# In this case we have multiple EXDATE definitions, one per line.
# Icalendar makes a list out of this instead of zipping it into one
# vDDDLists object. Actually, this feels correct for me, as it also
# allows to define different timezones per exdate line - but client
# code has to handle this as list and not blindly expecting to be able
# to call event['EXDATE'].to_ical() on it:
def test_exdate_formed_from_exdates_on_multiple_lines_is_a_list(events):
    exdate = events.event_with_recurrence_exdates_on_different_lines['exdate']
    assert isinstance(exdate, list)

@pytest.mark.parametrize('i, exception_date, exception_date_ics', [
    (0, datetime(2012, 5, 29, 10, 0), b'20120529T100000'),
    (1, datetime(2012, 4, 3, 10, 0),  b'20120403T100000'),
    (2, datetime(2012, 4, 10, 10, 0), b'20120410T100000'),
    (3, datetime(2012, 5, 1, 10, 0),  b'20120501T100000'),
    (4, datetime(2012, 4, 17, 10, 0), b'20120417T100000')
])
def test_list_exdate_to_ical_is_inverse_of_from_ical(events, i, exception_date, exception_date_ics, in_timezone):
    exdate = events.event_with_recurrence_exdates_on_different_lines['exdate']
    assert exdate[i].dts[0].dt == in_timezone(exception_date, 'Europe/Vienna')
    assert exdate[i].to_ical() == exception_date_ics

