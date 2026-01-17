===============
Event attendees
===============

This chapter explains how to use the event attendee information in iCalendar files with the icalendar library.
Attendees are present inside of events, alarms and other calendar components and occur as a :class:`~icalendar.prop.vCalAddress`. 

.. seealso::

    :class:`~icalendar.prop.vCalAddress`
    :attr:`Event.attendees <icalendar.cal.event.Event.attendees>`

Add attendees to an event
-------------------------

To add attendees to an event in icalendar, import the required classes.

.. code-block:: pycon

    >>> from icalendar import Event, vCalAddress, CUTYPE, ROLE, PARTSTAT

Then create the attendee object and set its parameters.

.. code-block:: pycon

    >>> attendee = vCalAddress.new(
    ...     "emily.smith@example.com",  # email address
    ...     cn="Emily Smith",           # common name
    ...     cutype=CUTYPE.INDIVIDUAL,   # calendar user type
    ...     role=ROLE.CHAIR,            # role
    ...     partstat=PARTSTAT.ACCEPTED, # participation status
    ...     rsvp=True,                  # RSVP requirement
    ... )

.. note::

    Apart from the email, all parameters are optional.
    Use the enumerations defined in :mod:`icalendar.enums` to ensure valid values.

Finally, add the attendee to the event.

.. code-block:: pycon

    >>> event = Event.new()
    >>> event.attendees = [attendee]    # set the attribute

The resulting event looks like this:

.. code-block:: pycon

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
In this example prints the email, common name, participation status, role, and RSVP requirement of each attendee.

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
