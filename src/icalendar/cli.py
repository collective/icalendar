#!/usr/bin/env python3
"""utility program that allows user to preview calendar's events"""
import sys
import pathlib
import argparse
from datetime import datetime

from icalendar import Calendar, __version__

def _format_name(address):
    """Retrieve the e-mail and the name from an address.

    :arg an address object, e.g. mailto:test@test.test

    :returns str: The name and the e-mail address.
    """
    email = address.split(':')[-1]
    name = email.split('@')[0]
    if not email:
        return ''
    return f"{name} <{email}>"


def _format_attendees(attendees):
    """Format the list of attendees.

    :arg any attendees: Either a list, a string or a vCalAddress object.

    :returns str: Formatted list of attendees.
    """
    if isinstance(attendees, list):
        return '\n'.join(map(lambda s: s.rjust(len(s) + 5), map(_format_name, attendees)))
    return _format_name(attendees)

def view(event):
    """Make a human readable summary of an iCalendar file.

    :returns str: Human readable summary.
    """
    summary = event.get('summary', default='')
    organizer = _format_name(event.get('organizer', default=''))
    attendees = _format_attendees(event.get('attendee', default=[]))
    location = event.get('location', default='')
    comment = event.get('comment', '')
    description = event.get('description', '').split('\n')
    description = '\n'.join(map(lambda s: s.rjust(len(s) + 5), description))

    start = event.decoded('dtstart')
    if 'duration' in event:
        end = event.decoded('dtend', default=start + event.decoded('duration'))
    else:
        end = event.decoded('dtend', default=start)
    duration = event.decoded('duration', default=end - start)
    if isinstance(start, datetime):
        start = start.astimezone()
    start = start.strftime('%c')
    if isinstance(end, datetime):
        end = end.astimezone()
    end = end.strftime('%c')

    return f"""    Organizer: {organizer}
    Attendees:
{attendees}
    Summary    : {summary}
    Starts     : {start}
    End        : {end}
    Duration   : {duration}
    Location   : {location}
    Comment    : {comment}
    Description:
{description}"""

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('calendar_files', nargs='+', type=pathlib.Path)
    parser.add_argument('--output', '-o', type=argparse.FileType('w'), default=sys.stdout, help='output file')
    parser.add_argument('-v', '--version', action='version', version=f'{parser.prog} version {__version__}')
    argv = parser.parse_args()

    for calendar_file in argv.calendar_files:
        with open(calendar_file) as f:
            calendar = Calendar.from_ical(f.read())
            for event in calendar.walk('vevent'):
                argv.output.write(view(event) + '\n\n')

if __name__ == '__main__':
    main()
