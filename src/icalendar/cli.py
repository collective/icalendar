#!/usr/bin/env python3
"""utility program that allows user to preview calendar's events"""
import sys
import pathlib
import argparse
from datetime import datetime
from . import Calendar, __version__

_TEMPLATE = """Organiser: {organiser}
Attendees:
  {attendees}
Summary: {summary}
When: {time_from}-{time_to}
Location: {location}
Comment: {comment}
Description:

{description}

"""

def _format_name(address):
    """Retrieve the e-mail and optionally the name from an address.

    :arg vCalAddress address: An address object.

    :returns str: The name and optionally the e-mail address.
    """
    if not address:
        return ''

    email = address.title().split(':')[1]
    if 'cn' in address.params:
        return '{} <{}>'.format(address.params['cn'], email)

    return email

def _format_attendees(attendees):
    """Format the list of attendees.

    :arg any attendees: Either a list, a string or a vCalAddress object.

    :returns str: Formatted list of attendees.
    """
    if isinstance(attendees, list):
        return '\n  '.join(map(_format_name, attendees))
    return _format_name(attendees)

def view(input_handle, output_handle):
    """Make a human readable summary of an iCalendar file.

    :arg stream handle: Open readable handle to an iCalendar file.

    :returns str: Human readable summary.
    """
    cal = Calendar.from_ical(input_handle.read())

    for event in cal.walk('vevent'):
        output_handle.write(_TEMPLATE.format(
            organiser=_format_name(event.get('organizer', '')),
            attendees=_format_attendees(event.get('attendee')),
            summary=event.get('summary', ''),
            time_from=datetime.strftime(
                event.get('dtstart').dt, '%a %d %b %Y %H:%M'),
            time_to=datetime.strftime(event.get('dtend').dt, '%H:%M'),
            location=event.get('location', ''),
            comment=event.get('comment', ''),
            description=event.get('description', '')).encode('utf-8'))

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('calendar_files', nargs='+', type=pathlib.Path)
    parser.add_argument('-v', '--version', action='version', version=f'{parser.prog} version {__version__}')
    argv = parser.parse_args()

    try:
        args.func(**{k: v for k, v in vars(args).items() if k not in ('func', 'subcommand')})
    except ValueError as error:
        parser.error(error)

if __name__ == '__main__':
    main()

