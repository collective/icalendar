========
Glossary
========

.. glossary::
    :sorted:

    icalendar
        This Python package, with a lower-case "c", used for parsing and generating :term:`iCalendar` files following the standard in :rfc:`5545`.

    iCalendar
        The RFC called Internet Calendaring and Scheduling Core Object Specification (iCalendar), with an upper-case "C".
        Files that follow the iCalendar specification are called iCalendar files.

    Vale
        `Vale <https://vale.sh/>`_ is an open-source, command-line tool that helps maintain a consistent and on-brand voice in documentation.
        icalendar documentation uses it to check spelling, English grammar and syntax, and style guides.

    properties
    property
        A property in an iCalendar file is the definition of an individual attribute describing a calendar object or a calendar :term:`component`.
        A property takes the form defined by the "contentline" notation defined in :rfc:`5545#section-3.1`.

        The body of an iCalendar file consists of a sequence of calendar properties and one or more calendar components.

        ..  seealso::

            :rfc:`5545#section-3.5`

    components
    component
        The body of the iCalendar object consists of a sequence of calendar :term:`properties` and one or more calendar components.
        The calendar properties are attributes that apply to the calendar object as a whole.
        The calendar components are collections of properties that express a particular calendar semantic.
        For example, the calendar component can specify an event, a to-do, a journal entry, time zone information, free/busy time information, or an alarm.

        All calendar components start with the letter "V".
        For example, "VEVENT" refers to the event calendar component.

        ..  seealso::

            :rfc:`5545#section-3.6`
