========
Glossary
========

.. glossary::
    :sorted:

    icalendar
        This Python package, with a lower-case "c", used for parsing and generating :term:`iCalendar` files following :doc:`various RFC standards <rfc-support>`.

    iCalendar
        The RFC called :rfc:`Internet Calendaring and Scheduling Core Object Specification (iCalendar)<5545>`, with an upper-case "C".
        Files that follow the iCalendar specification are called :term:`iCalendar files`.

    iCalendar file
    iCalendar files
        A file with :term:`iCalendar` content.
        The file name extension is ``ics``.

    xCal
        The RFC called :rfc:`xCal: The XML Format for iCalendar <6321>`, with an upper-case "C".
        Files that follow the xCal specification are called :term:`xCal files`.

    xCal file
    xCal files
        A file with :term:`xCal` content.
        No file name extension is standardized.
        :term:`icalendar` uses ``xml``.

    jCal
        The RFC called :rfc:`jCal: The JSON Format for iCalendar <7265>`, with an upper-case "C".
        Files that follow the jCal specification are called :term:`jCal files`.

    jCal file
    jCal files
        A file with :term:`iCalendar` content.
        The recommended file name extension is ``json``.
        :term:`icalendar` uses ``jcal`` in tests and examples.

    round-trip
        A round-trip happens when a calendar is converted into at least one other representation and back.
        Examples of a round-trip are:

        - A calendar file is read into icalendar and converted back to the original calendar file format.
        - A calendar is created with :meth:`Calendar.new <icalendar.cal.calendar.Calendar.new>`, converted to :term:`xCal` using :meth:`~icalendar.cal.component.Component.to_xcal`, and then read back into a :class:`~icalendar.cal.calendar.Calendar` object using :meth:`~icalendar.cal.component.Component.from_xcal`.

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
