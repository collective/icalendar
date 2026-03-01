=====
Usage
=====

This chapter describes how to use icalendar.

.. note::

    To avoid repetition, the code examples in this chapter use the following imports.

    .. code-block:: pycon

        >>> from icalendar import Calendar, Event


Components
----------

Components are case-insensitive Python dicts.
The ``Calendar`` object is a component.
The following example shows how to set two properties for it, then display them.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal["dtstart"] = "20050404T080000"
    >>> cal["summary"] = "Python meeting about calendaring"
    >>> for k,v in cal.items():
    ...     k,v
    ('DTSTART', '20050404T080000')
    ('SUMMARY', 'Python meeting about calendaring')

.. note::

    To add components to the calendar, create the :ref:`subcomponent <subcomponents>`, then add it via :meth:`icalendar.cal.component.Component.add()`.
    The example above adds a string, but not a ``vText`` component.

You can generate a string for a file with the :meth:`icalendar.cal.component.Component.to_ical` method.

.. code-block:: pycon

    >>> cal.to_ical()
    b'BEGIN:VCALENDAR\r\nDTSTART:20050404T080000\r\nSUMMARY:Python meeting about calendaring\r\nEND:VCALENDAR\r\n'

The rendered view is easier to read.

.. code-block:: pycon

    BEGIN:VCALENDAR
    DTSTART:20050404T080000
    SUMMARY:Python meeting about calendaring
    END:VCALENDAR

You can define a function to display :meth:`~icalendar.cal.component.Component.to_ical` output, as shown in the following example.

.. code-block:: pycon

    >>> def display(cal):
    ...    return cal.to_ical().decode("utf-8").replace("\r\n", "\n").strip()

You can set multiple properties, as shown in the following example.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal["attendee"] = ["MAILTO:maxm@mxm.dk","MAILTO:test@example.com"]
    >>> print(display(cal))
    BEGIN:VCALENDAR
    ATTENDEE:MAILTO:maxm@mxm.dk
    ATTENDEE:MAILTO:test@example.com
    END:VCALENDAR

If you don't want to care about whether a property value is a list or a single value, use the :meth:`icalendar.cal.component.Component.add()` method.
It will automatically convert the property to a list of values if more than one value is added.
Here is an example.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal.add("attendee", "MAILTO:maxm@mxm.dk")
    >>> cal.add("attendee", "MAILTO:test@example.com")
    >>> print(display(cal))
    BEGIN:VCALENDAR
    ATTENDEE:MAILTO:maxm@mxm.dk
    ATTENDEE:MAILTO:test@example.com
    END:VCALENDAR

.. note::

    This example doesn't check for compliance, so you should look in the :rfc:`5545` specification for legal properties for each component.
    You can also look in the :file:`icalendar/cal/calendar.py` file, where it is at least defined for each component.

.. note::

    icalendar automatically handles custom components (X-components and IANA-components) without special configuration.
    See :doc:`custom-components` for details on working with vendor-specific or non-standard components.


.. _subcomponents:

Subcomponents
-------------

Any component can have subcomponents.
For example, inside a calendar, there can be events.
They can be arbitrarily nested.

To demonstrate, first, make a new component.

.. code-block:: pycon

    >>> event = Event()
    >>> event["uid"] = "42"
    >>> event["dtstart"] = "20050404T080000"

Then append it to a parent.

.. code-block:: pycon

    >>> cal.add_component(event)
    >>> print(display(cal))
    BEGIN:VCALENDAR
    ATTENDEE:MAILTO:maxm@mxm.dk
    ATTENDEE:MAILTO:test@example.com
    BEGIN:VEVENT
    DTSTART:20050404T080000
    UID:42
    END:VEVENT
    END:VCALENDAR

Subcomponents are appended to the subcomponents property on the component.

.. code-block:: pycon

    >>> cal.subcomponents
    [VEVENT({'UID': '42', 'DTSTART': '20050404T080000'})]


Value types
-----------

Property values are UTF-8 encoded strings.

This is impractical if you want to use the data for further computation.
The datetime format, for example, looks like `20050404T080000`.
icalendar can parse and generate iCalendar formatted strings.

You can either use the :meth:`~icalendar.cal.component.Component.add()` method to do the work, or you can do it manually.

To add a datetime value, you can use Python's built in :mod:`datetime` types, and the set the encode parameter to ``True``, and it will convert to the type defined in the specification.

.. code-block:: pycon

    >>> from datetime import datetime
    >>> cal.add("dtstart", datetime(2005,4,4,8,0,0))
    >>> cal["dtstart"].to_ical()
    b'20050404T080000'

If that doesn't work satisfactorily for some reason, you can also do it manually.

In :file:`icalendar/prop.py`, all the iCalendar data types are defined.
Each type has a class that can parse and encode the type.

Thus, to parse it manually, you would do the following.

.. code-block:: pycon

    >>> from icalendar import vDatetime
    >>> now = datetime(2005,4,4,8,0,0)
    >>> vDatetime(now).to_ical()
    b'20050404T080000'

To summarize, initialize the object with a Python built in type, then call the :meth:`~icalendar.cal.component.Component.to_ical` method on the object.
That will return an iCal-encoded string.

You can do it the other way around, too.
To parse an encoded string, call the :meth:`~icalendar.cal.component.Component.from_ical` method, and it will return an instance of the corresponding Python type.

.. code-block:: pycon

    >>> vDatetime.from_ical("20050404T080000")
    datetime.datetime(2005, 4, 4, 8, 0)

    >>> vDatetime.from_ical("20050404T080000Z")
    datetime.datetime(2005, 4, 4, 8, 0, tzinfo=ZoneInfo(key='UTC'))

You can also choose to use the :meth:`icalendar.cal.component.Component.decoded` method, which will return a decoded value directly.


.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal.add("dtstart", datetime(2005,4,4,8,0,0))
    >>> cal["dtstart"].to_ical()
    b'20050404T080000'
    >>> cal.decoded("dtstart")
    datetime.datetime(2005, 4, 4, 8, 0)


Property parameters
-------------------

Property parameters are automatically added, depending on the input value.
For example, for date or time related properties, the value type and timezone identifier, if applicable, are automatically added.

.. code-block:: pycon

    >>> import zoneinfo
    >>> event = Event()
    >>> event.add("dtstart", datetime(2010, 10, 10, 10, 0, 0,
    ...                               tzinfo=zoneinfo.ZoneInfo("Europe/Vienna")))

    >>> lines = event.to_ical().splitlines()
    >>> assert (
    ...     b'DTSTART;TZID=Europe/Vienna:20101010T100000'
    ...     in lines)


You can also add arbitrary property parameters by passing a parameters dictionary to the :meth:`~icalendar.cal.component.Component.add()` method as shown.

.. code-block:: pycon

    >>> event = Event()
    >>> event.add("X-TEST-PROP", "tryout.",
    ...           parameters={"prop1":"val1", "prop2":"val2"})
    >>> lines = event.to_ical().splitlines()
    >>> assert b'X-TEST-PROP;PROP1=val1;PROP2=val2:tryout.' in lines


Examples
--------

This section describes how to use icalendar's essential features.


Read calendar from file
'''''''''''''''''''''''

Read a calendar from a local :file:`.ics` file and view its events.

.. code:: pycon

    >>> import icalendar
    >>> from pathlib import Path
    >>> ics_path = Path("src/icalendar/tests/calendars/example.ics")
    >>> calendar = icalendar.Calendar.from_ical(ics_path)
    >>> for event in calendar.events:
    ...     print(event.get("SUMMARY"))
    New Year's Day
    Orthodox Christmas
    International Women's Day


Read calendar from URL
''''''''''''''''''''''

To read a calendar from a URL, retrieve the data first, then parse it in icalendar.

.. code-block:: python

    from urllib.request import urlopen
    url = "https://www.gov.uk/bank-holidays/england-and-wales.ics"
    ics_data = urlopen(url).read()
    calendar = icalendar.Calendar.from_ical(ics_data)


Modify content
''''''''''''''

After loading the example file, edit and save it.

.. code:: pycon

    >>> calendar.calendar_name = "My Modified Calendar"  # modify
    >>> print(calendar.to_ical()[:121])  # save modification
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:collective/icalendar
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    NAME:My Modified Calendar


iCalendar objects
'''''''''''''''''

``icalendar`` supports the creation and parsing of all kinds of objects in the :rfc:`5545` iCalendar standard.

.. seealso::

    For a complete list of all supported objects, see the :doc:`icalendar API reference guide <../reference/api/icalendar>`.


Events
``````

Show events.

.. code:: pycon

    >>> icalendar.Event()
    VEVENT({})


Free/busy times
```````````````

Show free/busy times.

.. code:: pycon

    >>> icalendar.FreeBusy()
    VFREEBUSY({})


To-do items
```````````

Show to-do items.

.. code:: pycon

    >>> icalendar.Todo()
    VTODO({})



Alarms
``````

Show alarms.

.. code:: pycon

    >>> icalendar.Alarm()
    VALARM({})


Journal entries
```````````````

Show journal entries.

.. code:: pycon

    >>> icalendar.Journal()
    VJOURNAL({})


timezone implementations
''''''''''''''''''''''''

You can localize your events to take place in different timezones.

icalendar supports multiple timezone implementations, including :mod:`zoneinfo`, `dateutil.tz <https://dateutil.readthedocs.io/en/latest/tz.html>`_, and `pytz <https://pypi.org/project/pytz/>`_.
To demonstrate icalendar's flexibility, the following example creates an event that uses all of the timezone implementations with the same result.

.. code:: pycon

    >>> import pytz, zoneinfo, dateutil.tz  # timezone libraries
    >>> import datetime, icalendar
    >>> e = icalendar.Event()
    >>> tz = dateutil.tz.tzstr("Europe/London")
    >>> e["X-DT-DATEUTIL"] = icalendar.vDatetime(datetime.datetime(2024, 6, 19, 10, 1, tzinfo=tz))
    >>> tz = pytz.timezone("Europe/London")
    >>> e["X-DT-USE-PYTZ"] = icalendar.vDatetime(datetime.datetime(2024, 6, 19, 10, 1, tzinfo=tz))
    >>> tz = zoneinfo.ZoneInfo("Europe/London")
    >>> e["X-DT-ZONEINFO"] = icalendar.vDatetime(datetime.datetime(2024, 6, 19, 10, 1, tzinfo=tz))
    >>> print(e.to_ical())  # the libraries yield the same result
    BEGIN:VEVENT
    X-DT-DATEUTIL;TZID=Europe/London:20240619T100100
    X-DT-USE-PYTZ;TZID=Europe/London:20240619T100100
    X-DT-ZONEINFO;TZID=Europe/London:20240619T100100
    END:VEVENT


``zoneinfo`` default implementation
'''''''''''''''''''''''''''''''''''

.. versionchanged:: 6.0.0

Version 6 of icalendar switches the default timezone implementation from ``pytz`` to :mod:`zoneinfo`.
This only affects you if you parse icalendar objects with :meth:`from_ical <icalendar.cal.component.Component.from_ical>`.
The functionality is extended and tested since 6.0.0 with both timezone implementations ``pytz`` and :mod:`zoneinfo`.

Since 6.0.0 by default, :mod:`zoneinfo` timezones are created.

.. code:: pycon

    >>> dt = icalendar.Calendar.example("timezoned").events[0].start
    >>> dt.tzinfo
    ZoneInfo(key='Europe/Vienna')

To continue to receive ``pytz`` timezones in parsed results, you can receive all the latest updates, and switch back to earlier behavior.

.. code:: pycon

    >>> icalendar.use_pytz()
    >>> dt = icalendar.Calendar.example("timezoned").events[0].start
    >>> dt.tzinfo
    <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>


Complete recurring meeting
''''''''''''''''''''''''''

This section shows how to create a complete and typical iCalendar file of a recurring meeting event, then add some properties to it, including a location, organizer, attendees, alarms, recurrence, and other properties.
This file can be loaded into any application that supports iCalendar files.

Initialize the calendar.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> from datetime import datetime
    >>> import zoneinfo

Add some properties to be compliant with :rfc:`5545`.

.. code-block:: pycon

    >>> cal.add("prodid", "-//My calendar product//mxm.dk//")
    >>> cal.add("version", "2.0")

At least one subcomponent is required for a calendar to be compliant.

.. code-block:: pycon

    >>> event = Event()
    >>> event.add("summary", "Python meeting about calendaring")
    >>> event.add("dtstart", datetime(2005,4,4,8,0,0,tzinfo=zoneinfo.ZoneInfo("UTC")))
    >>> event.add("dtend", datetime(2005,4,4,10,0,0,tzinfo=zoneinfo.ZoneInfo("UTC")))
    >>> event.add("dtstamp", datetime(2005,4,4,0,10,0,tzinfo=zoneinfo.ZoneInfo("UTC")))

Create a property with parameters.
Notice that they are an attribute on the value.

.. code-block:: pycon

    >>> from icalendar import vCalAddress, vText
    >>> organizer = vCalAddress("MAILTO:noone@example.com")

Automatic encoding is not yet implemented for parameter values, so you must use the ``v*`` types which you can import from the icalendar :mod:`icalendar.prop` module.

.. code-block:: pycon

    >>> organizer.params["cn"] = vText("Max Rasmussen")
    >>> organizer.params["role"] = vText("CHAIR")
    >>> event["organizer"] = organizer
    >>> event["location"] = vText("Odense, Denmark")

    >>> event["uid"] = "20050115T101010/27346262376@mxm.dk"
    >>> event.add("priority", 5)

    >>> attendee = vCalAddress("MAILTO:maxm@example.com")
    >>> attendee.params["cn"] = vText("Max Rasmussen")
    >>> attendee.params["ROLE"] = vText("REQ-PARTICIPANT")
    >>> event.add("attendee", attendee, encode=0)

    >>> attendee = vCalAddress("MAILTO:the-dude@example.com")
    >>> attendee.params["cn"] = vText("The Dude")
    >>> attendee.params["ROLE"] = vText("REQ-PARTICIPANT")
    >>> event.add("attendee", attendee, encode=0)

Add the event to the calendar.

.. code-block:: pycon

    >>> cal.add_component(event)

By extending the event with subcomponents, you can create multiple alarms.

.. code-block:: pycon

    >>> from icalendar import Alarm
    >>> from datetime import timedelta
    >>> alarm_1h_before = Alarm()
    >>> alarm_1h_before.add("action", "DISPLAY")
    >>> alarm_1h_before.add("trigger", timedelta(hours=-1))
    >>> alarm_1h_before.add("description", "Reminder: Event in 1 hour")
    >>> event.add_component(alarm_1h_before)

    >>> alarm_24h_before = Alarm()
    >>> alarm_24h_before.add("action", "DISPLAY")
    >>> alarm_24h_before.add("trigger", timedelta(hours=-24))
    >>> alarm_24h_before.add("description", "Reminder: Event in 24 hours")
    >>> event.add_component(alarm_24h_before)

You can even add a recurrence, either from a dictionary or a string.
Note that if you want to add the recurrence rule from a string, you must use the :class:`~icalendar.prop.recur.recur.vRecur` property.
Otherwise the rule will be escaped, making it invalid.

.. code-block:: pycon

    >>> event.add("rrule", {"freq": "daily"})

Write to disk.

.. code-block:: pycon

    >>> import tempfile, os
    >>> directory = tempfile.mkdtemp()
    >>> f = open(os.path.join(directory, "example.ics"), "wb")
    >>> f.write(cal.to_ical())
    733
    >>> f.close()

Print out the calendar.

.. code-block:: pycon

    >>> print(cal.to_ical().decode("utf-8")) # doctest: +NORMALIZE_WHITESPACE
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//My calendar product//mxm.dk//
    BEGIN:VEVENT
    SUMMARY:Python meeting about calendaring
    DTSTART:20050404T080000Z
    DTEND:20050404T100000Z
    DTSTAMP:20050404T001000Z
    UID:20050115T101010/27346262376@mxm.dk
    RRULE:FREQ=DAILY
    ATTENDEE;CN="Max Rasmussen";ROLE=REQ-PARTICIPANT:MAILTO:maxm@example.com
    ATTENDEE;CN="The Dude";ROLE=REQ-PARTICIPANT:MAILTO:the-dude@example.com
    LOCATION:Odense\, Denmark
    ORGANIZER;CN="Max Rasmussen";ROLE=CHAIR:MAILTO:noone@example.com
    PRIORITY:5
    BEGIN:VALARM
    ACTION:DISPLAY
    DESCRIPTION:Reminder: Event in 1 hour
    TRIGGER:-PT1H
    END:VALARM
    BEGIN:VALARM
    ACTION:DISPLAY
    DESCRIPTION:Reminder: Event in 24 hours
    TRIGGER:-P1D
    END:VALARM
    END:VEVENT
    END:VCALENDAR
    <BLANKLINE>


Examples in source code
-----------------------

The docstrings in the :mod:`icalendar` package API documentation provide other usage examples.

The `tests <https://github.com/collective/icalendar/tree/main/src/icalendar/tests>`_ of icalendar also have more examples.

Miscellaneous examples
----------------------

This section describes how to solve specific usage issues with icalendar.
Post your usage question to the `icalendar discussion Q&A category <https://github.com/collective/icalendar/discussions/categories/q-a>`_.
You may :doc:`contribute answered questions to this section of the documentation <../contribute/documentation/index>` through a pull request, too.

Convert iCalendar to JSON
'''''''''''''''''''''''''

See the :doc:`jcal` documentation for how to convert iCalendar data to JSON.

Print event information
'''''''''''''''''''''''

To print all events of an iCalendar, iterate through them and print each as shown.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example()  # open a calendar
    >>> for event in calendar.events:  # iterate over all events
    ...     print(event.summary)
    New Year's Day
    Orthodox Christmas
    International Women's Day

.. seealso::

    -   :attr:`Calendar.events <icalendar.cal.calendar.Calendar.events>`
    -   :attr:`~icalendar.cal.component.Component.subcomponents`
    -   :meth:`~icalendar.cal.component.Component.walk`

Modify specific events
''''''''''''''''''''''

To find :attr:`~icalendar.cal.component.Component.subcomponents` that match specific requirements, use :meth:`~icalendar.cal.component.Component.walk`.

The following example filters through all subcomponents of the calendar, and if they have a specific word ``Christmas`` in their summary, makes the summary uppercase.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example()  # open a calendar
    >>> find_christmas = lambda c: "christmas" in c.get("SUMMARY", "").lower()
    >>> for component in calendar.walk(select=find_christmas):
    ...     component["SUMMARY"] = component["SUMMARY"].upper()
    >>> print(calendar.events[1].summary)
    ORTHODOX CHRISTMAS

Add timezones to a calendar
'''''''''''''''''''''''''''

Dates with times in icalendar can be timezone specific.
``UTC`` is such a timezone.
Other examples are ``Europe/Berlin``, ``America/New_York``, and ``Asia/Tokyo``.

The following example creates a calendar with an event in ``Europe/Zurich``, and adds all needed timezones just before saving the calendar.

.. code-block:: pycon

    >>> from icalendar import Calendar, Event
    >>> from datetime import datetime
    >>> from zoneinfo import ZoneInfo
    >>> event = Event.new(
    ...     summary="Meeting in Zurich",
    ...     start=datetime(2022, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Europe/Zurich")),
    ...     end=datetime(2022, 1, 1, 13, 0, 0, tzinfo=ZoneInfo("Europe/Zurich")),
    ...     location="Zurich, Switzerland",
    ... )
    >>> calendar = Calendar.new(
    ...     subcomponents=[event],
    ... )
    >>> calendar.add_missing_timezones()
    >>> 'Europe/Zurich' in [tz.tz_name for tz in calendar.timezones]
    True

After running :meth:`~icalendar.cal.calendar.Calendar.add_missing_timezones`, the calendar now contains all needed timezones and can be saved as a file with :meth:`~icalendar.cal.component.Component.to_ical`.
