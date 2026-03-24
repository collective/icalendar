===========================
Create event with attendees
===========================

In this tutorial, you'll create an iCalendar file with events and attendees.

Creating a calendar
-------------------

First, you create a :class:`~icalendar.cal.calendar.Calendar`, the highest component type which can contain one or more subcomponents.
The Calendar component itself contains its own properties.
When you create one using the :meth:`~icalendar.cal.calendar.Calendar.new()` method, it automatically sets the minimal required properties.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.new()

After creating a new calendar, you can view its properties by using :meth:`~icalendar.cal.component.Component.to_ical()`, which generates a bytes object of the component, and :meth:`~bytes.decode`, which converts the output to Unicode, making it easier to read.

..  code-block:: pycon

    >>> print(calendar.to_ical().decode())
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//collective//icalendar//7.0.0//EN
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    END:VCALENDAR

Notice that by default a calendar contains the version, product identifier (``PRODID``), and a unique identifier (``UID``).
All these properties are required for a calendar.
You can also set and change these properties.

.. code-block:: pycon

    >>> calendar.prodid = "-//icalendar//example.com//EN" 

Here you change the product identifier and print the revised component.
The output confirms the change:

.. code-block:: pycon

    >>> print(calendar.to_ical().decode())
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//icalendar//example.com//EN
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    END:VCALENDAR

Adding an event
---------------

Now that you have a base calendar, you can add an event to it.
You can similarly create an :class:`~icalendar.cal.event.Event` subcomponent using the :meth:`~icalendar.cal.event.Event.new()` method, which includes appropriate defaults.
You can also set these properties on creation.

.. code-block:: pycon

    >>> from icalendar import Event
    >>> import datetime as dt
    >>> import zoneinfo
    >>>
    >>> event = Event.new(
    ...     start=dt.datetime(2026, 3, 21, 6, 30,0, tzinfo=zoneinfo.ZoneInfo("UTC")),
    ...     end=dt.datetime(2026, 3, 21, 7, 30,0, tzinfo=zoneinfo.ZoneInfo("UTC")),
    ... )

This creates an event with a start and end date and time defined using :class:`~datetime.datetime` with a timezone.
The output shows your new event:

.. code-block:: pycon

    >>> print(event.to_ical().decode())
    BEGIN:VEVENT
    DTSTART:20260321T063000Z
    DTEND:20260321T073000Z
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    END:VEVENT

Notice that the event component includes the start and end dates with their times (``DTSTART`` and ``DTEND``) along with a unique identifier (``UID``), and its creation timestamp (``DTSTAMP``).

Similar to the calendar event, you can edit these properties or add new ones.

.. code-block:: pycon

    >>> event.summary = "Pick up bicycle from the workshop."

Using the :meth:`~icalendar.cal.component.Component.add()` method on a component, you can add new properties with their name and value.
The summary property represents the title of an event.

To use an event, you must add it to the calendar.

.. code-block:: pycon

    >>> calendar.add_component(event)

You can add the newly created event to the previously created calendar using :meth:`~icalendar.cal.component.Component.add_component()`.
Now print the calendar to verify everything that it contains:

.. code-block:: pycon

    >>> print(calendar.to_ical().decode())
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//icalendar//example.com//EN
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    BEGIN:VEVENT
    SUMMARY:Pick up bicycle from the workshop.
    DTSTART:20260321T063000Z
    DTEND:20260321T073000Z
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    END:VEVENT
    END:VCALENDAR

You can now see your calendar with the event nested inside.

Creating events with attendees
------------------------------

Next, create a second event in your calendar that includes attendees.

.. code-block:: pycon

    >>> from icalendar import vCalAddress
    >>> ride_event = Event.new(
    ...     start=dt.datetime(2026, 3, 28, 7, 00, 0, tzinfo=zoneinfo.ZoneInfo("UTC")),
    ...     end=dt.datetime(2026, 3, 28, 13, 30, 0, tzinfo=zoneinfo.ZoneInfo("UTC")),
    ...     summary="Morning ride with the team.",
    ...     attendees=[
    ...         vCalAddress("mailto:me@example.com"),
    ...         vCalAddress("mailto:another_friend@example.com"),
    ...     ]
    ... )

You've now created an event with a set start and end date and time, including a timezone, the event has a title, and lists two attendees by their email address.
The output confirms your additions:

.. code-block:: pycon

    >>> print(ride_event.to_ical().decode())
    BEGIN:VEVENT
    SUMMARY:Morning ride with the team.
    DTSTART:20260328T070000Z
    DTEND:20260328T133000Z
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    ATTENDEE:mailto:me@example.com
    ATTENDEE:mailto:another_friend@example.com
    END:VEVENT

You can see that both attendees were added to the event, along with the custom start and end timestamps.

You can also update the list of attendees after you created the event to add new attendees.

.. code-block:: pycon

    >>> ride_event.attendees.append(vCalAddress("mailto:late_joiner@example.com"))

Lastly, add this event to the same calendar you created in the beginning.

.. code-block:: pycon

    >>> calendar.add_component(ride_event)

Now print the calendar to view everything you've added so far, this should include the calendar component with two events.

.. code-block:: pycon

    >>> print(calendar.to_ical().decode())
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//icalendar//example.com//EN
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    BEGIN:VEVENT
    SUMMARY:Pick up bicycle from the workshop.
    DTSTART:20260321T063000Z
    DTEND:20260321T073000Z
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    END:VEVENT
    BEGIN:VEVENT
    SUMMARY:Morning ride with the team.
    DTSTART:20260328T070000Z
    DTEND:20260328T133000Z
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    ATTENDEE:mailto:me@example.com
    ATTENDEE:mailto:another_friend@example.com
    ATTENDEE:mailto:late_joiner@example.com
    END:VEVENT
    END:VCALENDAR

Creating an .ics file
---------------------

Now that you have finished creating your calendar, you can write it to a file.

.. code-block:: pycon

    >>> from pathlib import Path
    >>> path = Path("example.ics")
    >>> path.write_bytes(calendar.to_ical())
    611

This creates a new file called :download:`example.ics` and writes the bytes object returned by :meth:`~icalendar.cal.component.Component.to_ical()` to the file.

Look on your file system for the file, local to where you issued commands.
Its contents should be the following.

..  literalinclude:: example.ics
    :language: ics