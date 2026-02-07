==========
API design
==========

The components have different levels of API access to properties, subcomponents and parameters.

.. _property-access:

Property access
===============

Accessing components by their properties is preferred over using the :ref:`dictionary-access` for the following reasons.

* Values are checked for correctness.
* Values are converted to the correct type.
* Properties and parameters are typed for type checking and auto completion in editors when writing code that uses the icalendar package.
* Default values require fewer logical coding checks for presence.

The example below creates an event with useful default values, using :meth:`~icalendar.cal.event.Event.new`.
:rfc:`5545` requires ``DTSTAMP`` and ``UID`` values to be present, and if not set, they are automatically added.


.. code-block:: pycon
    :emphasize-lines: 3-6, 11-12

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

Lower case properties
---------------------

Lower case properties refer to the calculated attributes of the component, but not to the iCalendar :rfc:`5545` property name.

Continuing from the previous example, the next example shows how to access values by attributes.

.. code-block:: pycon

    >>> print(event.summary)
    New Year's Day Celebration

While some values are not set, they can be calculated from other values.
The event in this example has a duration of one day.

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

Upper case properties
---------------------

Upper case properties refer to both the component properties and the iCalendar :rfc:`5545` property name.
They're empty, or :obj:`None` if they're not set.
They can be accessed as attributes.

.. code-block:: pycon

    >>> event.DTSTART
    datetime.date(2022, 1, 1)
    >>> print(event.DURATION)
    None
    >>> print(event.DTEND)
    None

.. _parameter-properties:

Parameter properties
--------------------

Parameters can be accessed using specified properties.

The following example creates a new attendee for the previously created event from above.

.. code-block:: pycon

    >>> from icalendar import vCalAddress, ROLE
    >>> attendee = vCalAddress.new(
    ...     "maxm@example.com",
    ...     cn="Max Rasmussen",
    ...     role=ROLE.REQ_PARTICIPANT
    ... )
    >>> print(attendee.ROLE)
    REQ-PARTICIPANT

Similar to the casing of names of properties, lower case parameters calculate the property, whereas capital case parameters directly access the iCalendar property.

.. code-block:: pycon
    
    >>> print(attendee.email)  # calculated
    maxm@example.com
    >>> print(attendee.CN)  # direct access
    Max Rasmussen

The parameters turn up the iCal representation.

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

.. _dictionary-access:

Dictionary access
=================

The lowest level is the dictionary interface.
It is stable since version 4.0.

Although it's possible to directly set :obj:`str` values, it's preferred to use :meth:`~icalendar.cal.component.Component.add()` instead.
As mentioned in :ref:`property-access` above, some properties won't get set or validated through this method.

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
All keys are case insensitive.
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
:class:`~icalendar.prop.vText` is used for ``VERSION``, ``PRODID``, and ``DESCRIPTION``.
Preferably, use the :ref:`parameter-properties` to get and set the values.
You can also access them using ``.params``.

The following example sets the ``DESCRIPTION`` from  :rfc:`7986#section-5.1`, and adds a ``LANGUAGE`` parameter:

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
