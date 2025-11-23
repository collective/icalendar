===============
jCal - RFC 7265
===============

.. py:module:: icalendar

:rfc:`7265` specifies how to convert iCalendar to jCal, a JSON based representation.


Read jCal input
===============

Jcal is a JSON based representation of iCalendar.
The following calendar contains one event.

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

:meth:`Component.from_jcal` can be used to parse the :py:class:`list` or JSON :py:class:`str`.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.from_jcal(jCal)

After parsing the calendar, it can be inspected and altered.


.. code-block:: pycon

    >>> print(calendar.prodid)
    -//Example Inc.//Example Calendar//EN
    >>> print(calendar.events[0].summary)
    Planning meeting


Write jCal output
=================

You can convert a :class:`Calendar` and any other :class:`Component` to jCal using the :meth:`~Component.to_jcal` method.

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

You can directly generate JSON output and write it to a file or send it to a server using :meth:`~Component.to_json`.
Below, we write the jCal version of the calendar to a temporary file.

.. code-block:: pycon

    >>> from tempfile import NamedTemporaryFile
    >>> file = NamedTemporaryFile(suffix=".jcal")
    >>> file.write(calendar.to_json().encode("UTF-8"))
    358

