==========
API Design
==========

The components have different levels of API access to properties, subcomponents and parameters.

Property access
===============

Accessing components by their properties is preferred over using the `Dictionary access`_.

* Values are checked for correctness.
* Values are converted to the correct type.
* Properties and parameters are typed for type checking and auto-completion.
* Default values require less if/else checks for presence.

Below, we create an event with useful default values, using :meth:`~icalendar.cal.event.Event.new`.
:rfc:`5545` requires ``DTSTAMP`` and ``UID`` values to be present and if not set, they are automatically added.


.. code-block:: pycon

    >>> from icalendar import Event
    >>> from datetime import date
    >>> event = Event.new(
    ...     summary="New Year's Day Celebration",
    ...     start=date(2022, 1, 1)
    ... )
    >>> print(event.to_ical())
    BEGIN:VEVENT
    SUMMARY:New Year's Day Celebration
    DTSTART;VALUE=DATE:20220101
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    END:VEVENT

Lowercase properties
--------------------

You can access values by attributes.

.. code-block:: pycon

    >>> print(event.summary)
    New Year's Day Celebration

While some values are not set, they can calculated from other values.
The event in our example is one day long.

.. code-block:: pycon

    >>> event.start
    datetime.date(2022, 1, 1)
    >>> event.duration
    datetime.timedelta(days=1)
    >>> event.end
    datetime.date(2022, 1, 2)

While some attributes might be empty, they can have useful default values.

.. code-block:: pycon

    >>> event.rdates  # no RDATE is set
    []

Capital case properties
-----------------------

Some attributes are capital case.
They refer to the property name.
They are empty or :obj:`None` if they are not set.

.. code-block:: pycon

    >>> event.DTSTART
    datetime.date(2022, 1, 1)
    >>> print(event.DURATION)
    None
    >>> print(event.DTEND)
    None

Parameter properties
--------------------

Parameters can be accessed using specified properties.

In this example, we create a new attendee for the event.

.. code-block:: pycon

    >>> from icalendar import vCalAddress, ROLE
    >>> attendee = vCalAddress.new(
    ...     "maxm@example.com",
    ...     cn="Max Rasmussen",
    ...     role=ROLE.REQ_PARTICIPANT
    ... )
    >>> print(attendee.ROLE)
    REQ-PARTICIPANT

As with properties, some parameters are calculated (lower case) and some
are directly accessing the parameters (capital case).

.. code-block:: pycon
    
    >>> print(attendee.email)  # calculated
    maxm@example.com
    >>> print(attendee.CN)  # direct access
    Max Rasmussen

The parameters turn up the the ical representation.

.. code-block:: pycon
    
    >>> event.attendees = [attendee]
    >>> print(event.to_ical())
    BEGIN:VEVENT
    SUMMARY:New Year's Day Celebration
    DTSTART;VALUE=DATE:20220101
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    ATTENDEE;CN="Max Rasmussen";ROLE=REQ-PARTICIPANT:mailto:maxm@example.com
    END:VEVENT

Dictionary access
=================

The lowest level is the dictionary interface.
It is stable since version 4.0.

While you can set :obj:`str` values directly, is is recommended to use
:meth:`~icalendar.cal.component.Component.add()`:

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar()  # create and empty calendar
    >>> calendar.add("prodid", "-//My calendar product//mxm.dk//")
    >>> calendar.add("version", "2.0")
    >>> print(calendar.to_ical())
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//My calendar product//mxm.dk//
    END:VCALENDAR

The component is a dictionary, so you can access properties by key.
All keys are **case insensitive**.
This is implemented in :class:`~icalendar.caselessdict.CaselessDict`.

.. code-block:: pycon

    >>> calendar["version"] == calendar["VERSION"]
    True

The values can be retrieved by using :meth:`~icalendar.cal.component.Component.get()`.
The values are encoded as property values specified in :mod:`icalendar.prop`.

.. code-block:: pycon

    >>> calendar.get("version")
    vText(b'2.0')
    >>> print(calendar.get("name"))
    None

Parameter dictionary
--------------------

All property values are defined in :mod:`icalendar.prop` and have parameters.
:class:`~icalendar.prop.vText` is used for ``VERSION``, ``PRODID``, ``DESCRIPTION``.
Preferably, use the `Parameter properties`_ to get and set the values.
You can also access them using ``.params``.

Here, we set the ``DESCRIPTION`` from  :rfc:`7986#section-5.1` and add a ``LANGUAGE`` parameter:

.. code-block:: pycon

    >>> from icalendar import vText
    >>> description = vText("This is my personal calendar.")
    >>> description.params["language"] = "en"  # set language to English
    >>> calendar["description"] = description
    >>> print(calendar.to_ical())
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//My calendar product//mxm.dk//
    DESCRIPTION;LANGUAGE=en:This is my personal calendar.
    END:VCALENDAR
