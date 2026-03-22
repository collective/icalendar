==========
API design
==========

This chapter describes the API design of icalendar.

icalendar's API aligns with iCalendar components and properties as defined in :rfc:`5545`.

At their core, iCalendar components are dictionaries with case insensitive keys.
The preferred way to access their values is through lower case properties as described in :ref:`property-access`.
Advantages and disadvantages of the other approaches are discussed below.


Components
==========

Components are the building blocks of an iCalendar file.
Typically, you would create a calendar, then create a component, such as an event, and add the event component to the calendar.
Components may be nested.

Components are represented in icalendar as Python classes.
icalendar offers shortcuts to import its classes.
This is the preferred, stable, public interface.
Avoid using their fully qualified Python path, as these paths may change, and break your project.


.. _property-access:

Property access
===============

As described in the foregoing section, icalendar builds components and subcomponents.
It then adds, modifies, or removes properties to components and subcomponents, all within the RFC requirements.
All property value data types specified by :rfc:`5545#section-3.3` and subsequent RFCs can be found in :mod:`icalendar.prop`.

Accessing components by their properties is preferred over using the :ref:`dictionary-access` for the following reasons.

* Values are checked for correctness.
* Values are converted to the correct type.
* Properties and parameters are typed for type checking and auto completion in editors when writing code that uses the icalendar package.
* Default values require fewer logical coding checks for presence.

The example below creates an event with useful default values, using :meth:`~icalendar.cal.event.Event.new`.
:rfc:`5545` requires ``DTSTAMP`` and ``UID`` values to be present.
They are automatically added.

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


Based on the created event above, the following example shows how to access values by their properties.

.. code-block:: pycon

    >>> print(event.summary)
    New Year's Day Celebration
    >>> print(event.start)
    2022-01-01

Property naming convention
==========================
Property names are either in lower case or upper case.

-   Upper case property names refer simultaneously to both the Python component property name and the iCalender :rfc:`5545` property name.
    For example, ``DTEND`` occurs in :rfc:`5545#section-3.6.1` and as a property in :class:`~icalendar.cal.event.Event`.
-   Lower case property names refer to only the Python component property name.
    These properties are calculated from one or more upper case properties.
    For example, :attr:`~icalendar.cal.event.Event.end` is calculated either from :attr:`~icalendar.cal.event.Event.DTEND` or from both :attr:`~icalendar.cal.event.Event.DTSTART` and :attr:`~icalendar.cal.event.Event.DURATION`.

All properties can be accessed as attributes.


Lower case properties
---------------------

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

Upper case properties are either empty, or :obj:`None`, if they're not set.
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

Similar to the casing of names of properties, lower case parameters calculate the property, whereas upper case parameters directly access the iCalendar property.

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
:class:`~icalendar.prop.text.vText` is used for ``VERSION``, ``PRODID``, and ``DESCRIPTION``.
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


.. _import-shortcuts:

Import shortcuts
================

icalendar offers shortcuts to import its Python classes, which align with their counterpart iCalendar components.
The iCalendar :rfc:`5545` refers to components, such as events and alarms.
In the foregoing examples, you might have noticed imports such as the following.

..  code-block:: pycon

    >>> from icalendar import Event

By virtue of placing imports into each module's :file:`__init.py__` file, it brings in its Python classes and functions to the root of the icalendar package.
Without this convenience, imports would require the fully qualified Python path.

..  code-block:: pycon

    >>> from icalendar.cal.event import Event

This provides a nice API for developers, and establishes consistency across the API, ensuring backward compatibility as much as practical.
