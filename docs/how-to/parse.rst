.. _how-to-parse:

=========================
Parse any calendar format
=========================

This chapter describes how to parse calendar data when you do not know in advance whether it is iCalendar, jCal, or xCal.

icalendar supports three calendar formats, each with its own parser:

-   iCalendar, as specified in :rfc:`5545`, parsed by :meth:`Calendar.from_ical() <icalendar.cal.calendar.Calendar.from_ical>`
-   jCal, a JSON representation, as specified in :rfc:`7265`, parsed by :meth:`Calendar.from_jcal() <icalendar.cal.component.Component.from_jcal>`
-   xCal, an XML representation, as specified in :rfc:`6321`, parsed by :meth:`Calendar.from_xcal() <icalendar.cal.component.Component.from_xcal>`

The function :func:`~icalendar.cal.calendar.parse` detects the format for you and calls the matching parser.


Parse :class:`bytes`
====================

Pass the data as :class:`bytes`.

.. code-block:: pycon

    >>> from icalendar import parse
    >>> data = b'["vcalendar", [["prodid", {}, "text", "example"]], []]'
    >>> calendar = parse(data)
    >>> calendar["PRODID"]
    vText(b'example')

The format is detected from the first character, ignoring whitespace and a UTF-8 byte order mark:

-   ``B`` or ``b``, as in ``BEGIN:VCALENDAR``, means iCalendar.
-   ``[`` means jCal.
-   ``<`` means xCal.

If the format cannot be detected, :func:`~icalendar.cal.calendar.parse` raises :class:`~icalendar.error.UnknownCalendarFormat`.

.. code-block:: pycon

    >>> parse(b"not a calendar")
    Traceback (most recent call last):
      ...
    icalendar.error.UnknownCalendarFormat: Could not detect the calendar format: expected iCal, jCal or xCal data, but the data starts with b'n'.


Parse a file
============

Pass a :class:`~pathlib.Path` to read and parse a file.

.. code-block:: pycon

    >>> from pathlib import Path
    >>> calendar = parse(Path("src/icalendar/tests/calendars/example.ics"))
    >>> len(calendar.events)
    3

You can also pass a file that you opened in binary mode.

.. code-block:: pycon

    >>> with open("src/icalendar/tests/calendars/example.ics", "rb") as file:
    ...     calendar = parse(file)
    >>> len(calendar.events)
    3

A file opened in text mode returns :class:`str` instead of :class:`bytes`, so :func:`~icalendar.cal.calendar.parse` raises a :class:`TypeError`.


Parse several calendars
=======================

iCalendar and xCal data may contain several calendars.
jCal data always contains one calendar.
Most data contains only one calendar.

By default, :func:`~icalendar.cal.calendar.parse` returns one calendar.
If the data contains more than one calendar, returning only one of them would lose the others, so it raises :class:`~icalendar.error.CalendarInformationLost`.
If the data contains no calendars, it raises :class:`~icalendar.error.NoCalendarsFound`.

To get all calendars as a list, pass ``multiple=True``.

.. code-block:: pycon

    >>> ical = b"BEGIN:VCALENDAR\r\nPRODID:example\r\nEND:VCALENDAR\r\n"
    >>> calendars = parse(ical + ical, multiple=True)
    >>> len(calendars)
    2
