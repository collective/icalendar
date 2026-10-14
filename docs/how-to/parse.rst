Parsing calendars with ``icalendar.parse``
===========================================

The :func:`icalendar.parse` function provides a convenient way to load calendar
data from a variety of sources and formats (iCal, jCal, and xCal).

It automatically detects the format based on the first non-whitespace character
of the input:

- ``[`` → jCal
- ``<`` → xCal
- ``B`` (from ``BEGIN:VCALENDAR``) → iCal

Example
-------

.. code-block:: python

    from icalendar import parse

    # From bytes (iCal)
    calendar = parse(b"BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Example//EN\nEND:VCALENDAR")

    # From a file path
    calendar = parse("path/to/calendar.ics")

    # Return a list when multiple calendars may be present
    calendars = parse(source, multiple=True)

Parameters
----------

- ``source``: ``str``, ``bytes``, ``pathlib.Path``, or a file-like object containing calendar data.
- ``multiple``: If ``True``, always return a list of calendars. If ``False`` (default), return a single calendar.

Raises
------

- :class:`~icalendar.error.InvalidCalendar` if the input is empty or the format cannot be detected.
- Format-specific parsing errors (``JCalParsingError``, ``XCalParsingError``, ``ICalParsingError``).

See also
--------

- :meth:`Calendar.from_ical <icalendar.cal.Calendar.from_ical>`
- :meth:`Calendar.from_jcal <icalendar.cal.Component.from_jcal>`
- :meth:`Calendar.from_xcal <icalendar.cal.Component.from_xcal>`
