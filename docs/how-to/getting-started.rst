===============
Getting started
===============

This chapter will help you quicky get started using icalendar.

Creating a calendar
-------------------

A Calendaris the highest component type which can containe one ore more subcomponents. The calendar component itself also contains its own properties. By creating a calendar using the :meth:`~icalendar.cal.calendar.Calendar.new()` method we ensure the minimal required properties are set.

.. code-block:: py

    from icalendar import Calendar

    calendar = Calendar.new()
    print(calendar.to_ical().decode())

After creating a new calendar we can view its properties by using :meth:`~icalendar.cal.component.Component.to_ical()`, which generates a bytes object of the component, and ``decode()`` which converts the output to Unicode making it easier to read.

.. code-block::

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//collective//icalendar//7.0.2//EN
    UID:79f3cdd8-4562-4e06-9ea3-ac4fc5f6b802
    END:VCALENDAR

By default a calender contains the version, product identifier (``PRODID``), and a unique identifier (``UID``). All ofo which are required properties for a calendar. We can also set and change these properties.

.. code-block:: py

    calendar['PRODID'] = "-//icalendar//example.com//EN"
    print(cal.to_ical().decode())

Here we change the product identifier and print the revised component.

.. code-block::

    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//icalendar//example.com//EN
    UID:79f3cdd8-4562-4e06-9ea3-ac4fc5f6b802
    END:VCALENDAR

Adding an event
---------------

With the base calendar created, we can start to add events. An Event subcomponent can similarly be created using the :meth:`~icalendar.cal.event.Event.new()` method which includes appropriate defaults. However, we can also choose to set these properties on creation.

.. code-block:: py

    from icalendar import Event
    import datetime as dt
    import zoneinfo

    event = Event.new(
        start=dt.datetime(2026, 3, 21, 6, 30,0, tzinfo=zoneinfo.ZoneInfo('Europe/Berlin')),
        end=dt.datetime(2026, 3, 21, 7, 30,0, tzinfo=zoneinfo.ZoneInfo('Europe/Berlin')),
    )
    print(event.to_ical().decode())

This creates an event with a start and end time defined using datetime with a timezone. Using the same approach to print this component we can view our event.

.. code-block::

    BEGIN:VEVENT
    DTSTART;TZID=Europe/Berlin:20260321T063000
    DTEND;TZID=Europe/Berlin:20260321T073000
    DTSTAMP:20260301T104000Z
    UID:a3d2479f-7127-48e6-bbca-d9e0637f02b7
    END:VEVENT

The event component includes the start and end dates with their times (``DTSTART`` and ``DTEND``) along with a unique identifier (``UID``), and information about when this event was created (``DTSTAMP``).

Similarly to the calendar event we can edit these properties or add new ones.

.. code-block:: py

    event.add('summary', 'Pickup bicycle from the workshop.')

Using the :meth:`~icalendar.cal.component.Component.add()` method on a component we can add new properties with their name and value. The summary property represents the title of an event.

To use an event we must add it to the calendar.

.. code-block:: py

    calendar.add_component(event)
    print(calendar.to_ical().decode())

Our newly created event can be added to the previously created calendar using :meth:`~icalendar.cal.component.Component.add_component()`. We can then print out the calendar to verify everything it contains.

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

We can now see our calendar with the event nested inside.

Creating events with attendees
------------------------------

Now weare going to create a second event in our calendar which includes attendees.

.. code-block:: py

    ride_event = Event.new(
        start=dt.datetime(2026, 3, 28, 7, 00,0, tzinfo=zoneinfo.ZoneInfo('Europe/Berlin')),
        end=dt.datetime(2026, 3, 28, 13, 30,0, tzinfo=zoneinfo.ZoneInfo('Europe/Berlin')),
        summary="Morning ride with the team.",
        attendees=[
            vCalAddress("mailto:me@example.com"),
            vCalAddress("mailto:another_friend@example.com")
        ]
    )
    print(ride_event.to_ical().decode())

We have now created an event with a set start and end time, including a timezone, the event has a title and lists two attendees by their email address.

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

The ouput confirms both attendees were added to the event, along with the custom start and end timestamps.

The list of attendees can also be updated after the event was created to add new attendees.

.. code-block:: py

    ride_event.attendees.append(vCalAddress("mailto:late_joiner@example.com"))

Lastly, we can add this event to the same calendar we created in the beginning.

.. code-block:: py

    calendar.add_component(ride_event)

Creating an .ical file
----------------------

After we're complete with creating our calendar we can write our calendr to a file.

.. code-block:: py

    with open("example.ics", "wb") as f:
        f.write(calendar.to_ical())

This creates a new file called ``example.ics`` and writes the bytes objet returned by :meth:`~icalendar.cal.component.Component.to_ical()` to the file.
