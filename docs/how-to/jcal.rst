===============
jCal - RFC 7265
===============

.. py:module:: icalendar

This chapter describes how to read and write jCal files, and how to convert them between iCalendar files.

:rfc:`7265` specifies how to convert the iCalendar format to and from the jCal format, a JSON based representation.


Read jCal input
===============

The following jCal calendar contains one event.

.. code-block:: pycon

    >>> jCal = """
    ... ["vcalendar",
    ...   [
    ...     ["calscale", {}, "text", "GREGORIAN"],
    ...     ["prodid", {}, "text", "-//Example Inc.//Example Calendar//EN"],
    ...     ["version", {}, "text", "2.0"]
    ...   ],
    ...   [
    ...     ["vevent",
    ...       [
    ...         ["dtstamp", {}, "date-time", "2008-02-05T19:12:24Z"],
    ...         ["dtstart", {}, "date", "2008-10-06"],
    ...         ["summary", {}, "text", "Planning meeting"],
    ...         ["uid", {}, "text", "4088E990AD89CB3DBB484909"]
    ...       ],
    ...       []
    ...     ]
    ...   ]
    ... ]
    ... """

Use :meth:`Component.from_jcal` to parse the :py:class:`list` or JSON :py:class:`str`.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.from_jcal(jCal)

After parsing the calendar, inspect it as shown.

.. code-block:: pycon

    >>> print(calendar.prodid)
    -//Example Inc.//Example Calendar//EN
    >>> print(calendar.events[0].summary)
    Planning meeting


Write jCal output
=================

To convert a :class:`Calendar` and any other :class:`Component` to jCal, use the :meth:`~Component.to_jcal` method.

.. code-block:: pycon

    >>> from pprint import pprint
    >>> pprint(calendar.to_jcal())
    ['vcalendar',
     [['calscale', {}, 'text', 'GREGORIAN'],
      ['prodid', {}, 'text', '-//Example Inc.//Example Calendar//EN'],
      ['version', {}, 'text', '2.0']],
     [['vevent',
       [['dtstamp', {}, 'date-time', '2008-02-05T19:12:24Z'],
        ['dtstart', {}, 'date', '2008-10-06'],
        ['summary', {}, 'text', 'Planning meeting'],
        ['uid', {}, 'text', '4088E990AD89CB3DBB484909']],
       []]]]

To directly generate JSON output and write it to a file or send it to a server, use :meth:`~Component.to_json`.
The following commands writes the jCal version of the calendar to a temporary file.

.. code-block:: pycon

    >>> from tempfile import NamedTemporaryFile
    >>> file = NamedTemporaryFile(suffix=".jcal")
    >>> file.write(calendar.to_json().encode("UTF-8"))
    358
