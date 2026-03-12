===========================
Create event with attendees
===========================

In this tutorial, you'll create an iCalendar file with events and attendees.

Creating a calendar
-------------------

First, you create a :class:`~icalendar.cal.calendar.Calendar`, the highest component type which can contain one or more subcomponents.
The Calendar component itself contains its own properties.
When you create one using the :meth:`~icalendar.cal.calendar.Calendar.new()` method, it automatically sets the minimal required properties.

.. code-block:: py

    from icalendar import Calendar

    calendar = Calendar.new()
    print(calendar.to_ical().decode())

After creating a new calendar, you can view its properties by using :meth:`~icalendar.cal.component.Component.to_ical()`, which generates a bytes object of the component, and :meth:`~bytes.decode`, which converts the output to Unicode, making it easier to read.

..  code-block:: calendar

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//collective//icalendar//7.0.2//EN
    UID:79f3cdd8-4562-4e06-9ea3-ac4fc5f6b802
    END:VCALENDAR

Notice that by default a calendar contains the version, product identifier (``PRODID``), and a unique identifier (``UID``).
All these are required properties for a calendar.
You can also set and change these properties.

.. code-block:: py

    calendar['PRODID'] = "-//icalendar//example.com//EN"
    print(cal.to_ical().decode())

Here you change the product identifier and print the revised component.
The output confirms the change:

.. code-block::

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//icalendar//example.com//EN
    UID:79f3cdd8-4562-4e06-9ea3-ac4fc5f6b802
    END:VCALENDAR

Adding an event
---------------

Now that you have a base calendar, you can add an event to it.
You can similarly create an :class:`~icalendar.cal.event.Event` subcomponent using the :meth:`~icalendar.cal.event.Event.new()` method, which includes appropriate defaults.
You can also set these properties on creation.

.. code-block:: py

    from icalendar import Event
    import datetime as dt
    import zoneinfo

    event = Event.new(
        start=dt.datetime(2026, 3, 21, 6, 30,0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")),
        end=dt.datetime(2026, 3, 21, 7, 30,0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")),
    )
    print(event.to_ical().decode())

This creates an event with a start and end date and time defined using ``datetime`` with a timezone.
The output shows your new event:

.. code-block::

    BEGIN:VEVENT
    DTSTART;TZID=Europe/Berlin:20260321T063000
    DTEND;TZID=Europe/Berlin:20260321T073000
    DTSTAMP:20260301T104000Z
    UID:a3d2479f-7127-48e6-bbca-d9e0637f02b7
    END:VEVENT

Notice that the event component includes the start and end dates with their times (``DTSTART`` and ``DTEND``) along with a unique identifier (``UID``), and information about when this event was created (``DTSTAMP``).

Similar to the calendar event, you can edit these properties or add new ones.

.. code-block:: py

    event.add("summary", "Pickup bicycle from the workshop.")

Using the :meth:`~icalendar.cal.component.Component.add()` method on a component, you can add new properties with their name and value.
The summary property represents the title of an event.

To use an event, you must add it to the calendar.

.. code-block:: py

    calendar.add_component(event)
    print(calendar.to_ical().decode())

You can add the newly created event to the previously created calendar using :meth:`~icalendar.cal.component.Component.add_component()`.
Now print the calendar to verify everything that it contains:

.. code-block::

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//icalendar//example.com//EN
    UID:ac593e44-295f-41ef-9412-7fab970214be
    BEGIN:VEVENT
    SUMMARY:Pickup bicycle from the workshop.
    DTSTART;TZID=Europe/Berlin:20260321T063000
    DTEND;TZID=Europe/Berlin:20260321T073000
    DTSTAMP:20260301T104625Z
    UID:81fc98e2-46db-4506-b7bc-2177d4f2c469
    END:VEVENT
    END:VCALENDAR

You can now see your calendar with the event nested inside.

Creating events with attendees
------------------------------

Next, create a second event in your calendar that includes attendees.

.. code-block:: py

    ride_event = Event.new(
        start=dt.datetime(2026, 3, 28, 7, 00,0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")),
        end=dt.datetime(2026, 3, 28, 13, 30,0, tzinfo=zoneinfo.ZoneInfo("Europe/Berlin")),
        summary="Morning ride with the team.",
        attendees=[
            vCalAddress("mailto:me@example.com"),
            vCalAddress("mailto:another_friend@example.com")
        ]
    )
    print(ride_event.to_ical().decode())

You've now created an event with a set start and end date and time, including a timezone, the event has a title, and lists two attendees by their email address.
The output confirms your additions:

.. code-block::

    BEGIN:VEVENT
    SUMMARY:Morning ride with the team.
    DTSTART;TZID=Europe/Berlin:20260328T070000
    DTEND;TZID=Europe/Berlin:20260328T133000
    DTSTAMP:20260301T110629Z
    UID:6b5b4cb9-a99c-414b-ae43-1dd0a6b663e0
    ATTENDEE:mailto:me@example.com
    ATTENDEE:mailto:another_friend@example.com
    END:VEVENT

You can see that both attendees were added to the event, along with the custom start and end timestamps.

You can also update the list of attendees after you created the event to add new attendees.

.. code-block:: py

    ride_event.attendees.append(vCalAddress("mailto:late_joiner@example.com"))

Lastly, add this event to the same calendar you created in the beginning.

.. code-block:: py

    calendar.add_component(ride_event)

Creating an .ics file
---------------------

Now that you have finished creating your calendar, you can write it to a file.

.. code-block:: py

    with open("example.ics", "wb") as f:
        f.write(calendar.to_ical())

This creates a new file called :file:`example.ics` and writes the bytes object returned by :meth:`~icalendar.cal.component.Component.to_ical()` to the file.
