#!/usr/bin/env python3
"""utility program that allows user to preview calendar's events"""
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
    else:
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
    organiser = _format_name(event.get('organizer', default=''))
    attendees = _format_attendees(event.get('attendee', default=[]))
    location = event.get('location', default='')
    comment = event.get('comment', '')
    description = event.get('description', '').split('\n')
    description = '\n'.join(map(lambda s: s.rjust(len(s) + 5), description))

    timezone = datetime.utcnow().astimezone().tzinfo
    start = event.decoded('dtstart').astimezone(timezone).strftime('%c')
    end = event.decoded('dtstart', default=start).astimezone(timezone).strftime('%c')

    return f"""Organiser: {organiser}
    Attendees:
{attendees}
    Summary: {summary}
    When: {start} - {end}
    Location: {location}
    Comment: {comment}
    Description:
{description}
    """

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('calendar_files', nargs='+', type=pathlib.Path)
    parser.add_argument('-v', '--version', action='version', version=f'{parser.prog} version {__version__}')
    argv = parser.parse_args()

    for calendar_file in argv.calendar_files:
        with open(calendar_file) as f:
            calendar = Calendar.from_ical(f.read())
            for event in calendar.walk('vevent'):
                print(view(event))

if __name__ == '__main__':
    main()

