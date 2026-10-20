=========================
Parse any calendar format
=========================

This chapter describes how to parse calendar data when you do not know in advance whether it is iCalendar, jCal, or xCal.

icalendar supports three calendar formats:

-   iCalendar, as specified in :rfc:`5545`
-   jCal, a JSON representation, as specified in :rfc:`7265`
-   xCal, an XML representation, as specified in :rfc:`6321`

Each format has its own parser, such as :meth:`Calendar.from_ical() <icalendar.cal.calendar.Calendar.from_ical>`.
The function :func:`~icalendar.cal.calendar.parse` detects the format for you and calls the matching parser.


Parse data
==========

Pass the data as :class:`bytes`.

.. code-block:: pycon

    >>> from icalendar import parse
    >>> data = b'["vcalendar", [["prodid", {}, "text", "example"]], []]'
    >>> calendar = parse(data)
    >>> calendar["PRODID"]
    vText(b'example')

The format is detected from the first non-whitespace character:

-   ``B``, as in ``BEGIN:VCALENDAR``, means iCalendar.
-   ``[`` means jCal.
-   ``<`` means xCal.

If the format cannot be detected, :func:`~icalendar.cal.calendar.parse` raises a :class:`ValueError`.


Parse a file
============

Pass a :class:`~pathlib.Path` to read and parse a file.

.. code-block:: python

    from pathlib import Path
    from icalendar import parse

    calendar = parse(Path("calendar.ics"))

You can also pass a file that you opened in binary mode.

.. code-block:: python

    with open("calendar.ics", "rb") as file:
        calendar = parse(file)


Parse several calendars
=======================

By default, :func:`~icalendar.cal.calendar.parse` returns one calendar.
If the data contains more than one calendar, it raises a :class:`ValueError`.

To get all calendars as a list, pass ``multiple=True``.

.. code-block:: pycon

    >>> ical = b"BEGIN:VCALENDAR\r\nPRODID:example\r\nEND:VCALENDAR\r\n"
    >>> calendars = parse(ical + ical, multiple=True)
    >>> len(calendars)
    2
