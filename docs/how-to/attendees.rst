===============
Event attendees
===============

This chapter explains how to work with attendee information in iCalendar files using the icalendar library.
Each attendee is a :class:`~icalendar.prop.cal_address.vCalAddress`.
The components that support attendees are :class:`~icalendar.cal.event.Event`, :class:`~icalendar.cal.todo.Todo`, :class:`~icalendar.cal.journal.Journal`, and :class:`~icalendar.cal.alarm.Alarm`.
The examples below use :class:`~icalendar.cal.event.Event`, but the same attendee API applies to each of these components.

.. seealso::

    :attr:`Event.attendees <icalendar.cal.event.Event.attendees>`

Assign attendees to an event
----------------------------

Assign a single email string to :attr:`~icalendar.cal.event.Event.attendees` to set one attendee.
The string is converted to a :class:`~icalendar.prop.cal_address.vCalAddress` object.

.. code-block:: pycon

    >>> from icalendar import Event
    >>> event = Event.new()
    >>> event.attendees = "emily.smith@example.com"
    >>> event.attendees
    [vCalAddress('mailto:emily.smith@example.com')]

Assign a list of email strings to set several attendees at once.
A plain email address receives a ``mailto:`` prefix, while an address that already starts with ``mailto:`` is kept as is.

.. code-block:: pycon

    >>> event.attendees = [
    ...     "emily.smith@example.com",
    ...     "mailto:alex@example.com",
    ... ]
    >>> event.attendees
    [vCalAddress('mailto:emily.smith@example.com'), vCalAddress('mailto:alex@example.com')]

You can also pass attendee strings when creating the event with :meth:`Event.new <icalendar.cal.event.Event.new>`.
This is equivalent to assigning them afterward.

.. code-block:: pycon

    >>> event = Event.new(attendees="emily.smith@example.com")
    >>> event.attendees
    [vCalAddress('mailto:emily.smith@example.com')]

An attendee may carry parameters defined by :rfc:`5545#section-3.8.4.1`, such as ``CN``, ``ROLE``, and ``RSVP``.
Create such an attendee with :meth:`vCalAddress.new <icalendar.prop.cal_address.vCalAddress.new>`, whose Python keyword arguments ``cn``, ``role``, and ``rsvp`` set those RFC parameters.

.. code-block:: pycon

    >>> from icalendar import vCalAddress, CUTYPE, ROLE, PARTSTAT
    >>> attendee = vCalAddress.new(
    ...     "emily.smith@example.com",  # email address
    ...     cn="Emily Smith",           # CN parameter (common name)
    ...     cutype=CUTYPE.INDIVIDUAL,   # CUTYPE parameter (calendar user type)
    ...     role=ROLE.CHAIR,            # ROLE parameter
    ...     partstat=PARTSTAT.ACCEPTED, # PARTSTAT parameter (participation status)
    ...     rsvp=True,                  # RSVP parameter
    ... )

.. note::

    Apart from the email, all parameters are optional.
    Use the enumerations defined in :mod:`icalendar.enums` to ensure valid values.

Assign the attendee to the event.
Assigning a new value replaces any attendees that were set before.

.. code-block:: pycon

    >>> event = Event.new()
    >>> event.attendees = [attendee]    # set the attribute
    >>> print(event.to_ical())
    BEGIN:VEVENT
    DTSTAMP:20250517T080612Z
    UID:d755cef5-2311-46ed-a0e1-6733c9e15c63
    ATTENDEE;CN="Emily Smith";CUTYPE=INDIVIDUAL;PARTSTAT=ACCEPTED;ROLE=CHAIR;R
     SVP=TRUE:mailto:emily.smith@example.com
    END:VEVENT


Access attendee information
---------------------------

After parsing an iCalendar file with :meth:`Calendar.from_ical <icalendar.cal.calendar.Calendar.from_ical>`, access any of its events.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example("property_params")  # load a calendar
    >>> event = calendar.events[0]                      # get the first event

Events can have multiple attendees.
Access them using the :attr:`~icalendar.cal.event.Event.attendees` property.

.. code-block:: pycon

    >>> attendees = event.attendees  # get the attendees

The standard parameters of each attendee can be accessed as attributes.
The following example prints the email, common name, participation status, role, and RSVP requirement of each attendee.

.. code-block:: pycon

    >>> for attendee in attendees:
    ...     print("Email:", attendee.email)          # print the email
    ...     print("- CN:", attendee.CN)              # print the common name
    ...     print("- PARTSTAT:", attendee.PARTSTAT)  # print the participation status
    ...     print("- ROLE:", attendee.ROLE)          # print the role
    ...     print("- RSVP:", attendee.RSVP)          # print the RSVP requirement
    Email: rembrand@xs4all.nl
    - CN: RembrandXS
    - PARTSTAT: NEEDS-ACTION
    - ROLE: REQ-PARTICIPANT
    - RSVP: True
    Email: rembrand@daxlab.com
    - CN: RembrandDX
    - PARTSTAT: NEEDS-ACTION
    - ROLE: REQ-PARTICIPANT
    - RSVP: True
    Email: rembspam@xs4all.nl
    - CN: RembrandSB
    - PARTSTAT: NEEDS-ACTION
    - ROLE: REQ-PARTICIPANT
    - RSVP: True

All parameters can also be accessed using dictionary syntax.

.. code-block:: pycon

    >>> attendee = attendees[0]       # get the first attendee
    >>> print(attendee.params["CN"])  # print the common name
    RembrandXS
