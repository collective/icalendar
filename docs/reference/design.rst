======
Design
======

icalendar is used for parsing and generating iCalendar files following the standard in :rfc:`5545`.
It should be fully compliant, but it is possible to generate and parse invalid files if you want to.


Compatibility
-------------

icalendar is compatible with the following RFC standards.

:rfc:`2445`
    obsoleted by :rfc:`5545`
:rfc:`5545`
    Internet Calendaring and Scheduling Core Object Specification (iCalendar)
:rfc:`6868`
    Parameter Value Encoding in iCalendar and vCard
:rfc:`7529`
    Non-Gregorian Recurrence Rules in the Internet Calendaring and Scheduling Core Object Specification (iCalendar)
:rfc:`9074`
    "VALARM" Extensions for iCalendar
:rfc:`7953`
    Calendar Availability
:rfc:`7986`
    New Properties for iCalendar
:rfc:`9253`
    Support for iCalendar Relationships

The maintainers of icalendar do not claim compatibility with the following RFCs.
They might work though.

:rfc:`9073`
    Event Publishing Extensions to iCalendar


iCalendar file structure
------------------------

An iCalendar file is a text file with UTF-8 character encoding in a special format.

It consists of content lines, with each content line defining a property that has three parts: name, parameters, and values.
Parameters are optional.

The following examples illustrate the file structure.

The following example iCalendar file consists of a single content line, with only a name and value.

.. code-block:: text

    BEGIN:VCALENDAR

The next example iCalendar file consists of a content line with parameters.

.. code-block:: text

    ATTENDEE;CN=Max Rasmussen;ROLE=REQ-PARTICIPANT:MAILTO:example@example.com

In the previous iCalendar file example, its parts are the following.

Name
    ``ATTENDEE``
Params
    ``CN=Max Rasmussen;ROLE=REQ-PARTICIPANT``
Value
    ``MAILTO:example@example.com``

For long content lines, icalendar usually "folds" them to less than 75 characters.

On a higher level, you can think of an iCalendar file's structure as having components and subcomponents.

A component will have properties with values.
The values have special types, including integer, text, and datetime.
These values are encoded in a special text format in an iCalendar file.
icalendar contains methods for converting to and from these encodings.

The following example is a ``VCALENDAR`` component representing a calendar.

.. code-block:: text

    BEGIN:VCALENDAR
    ... vcalendar properties ...
    END:VCALENDAR

The most frequent subcomponent to a ``VCALENDAR`` component is a ``VEVENT``.
This following example is a ``VCALENDAR`` component with a nested ``VEVENT`` subcomponent.

.. code-block:: text

    BEGIN:VCALENDAR
    ... vcalendar properties ...
    BEGIN:VEVENT
    ... vevent properties ...
    END:VEVENT
    END:VCALENDAR
