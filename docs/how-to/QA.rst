==========
How do I …
==========

This document collects questions and their answers about how to solve a specific problem with icalendar.


… convert icalendar to JSON?
============================

The :doc:`jcal` documentation answers this question.

… print event information?
==========================

You can iterate over all events of icalendar, and print them like this:

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example()  # open a calendar
    >>> for event in calendar.events:  # iterate over all events
    ...     print(event.summary)
    New Year's Day
    Orthodox Christmas
    International Women's Day

.. seealso::

    :attr:`Calendar.events <icalendar.cal.calendar.Calendar.events>`
    :attr:`~icalendar.cal.component.Component.subcomponents`
    :meth:`~icalendar.cal.component.Component.walk`

… modify specific events?
=========================

To find :attr:`~icalendar.cal.component.Component.subcomponents` that match specific requirements,
you can use :meth:`~icalendar.cal.component.Component.walk`.

In this example, we filter through all subcomponents of the calendar,
and if they have a specific word ``Christmas`` in their summary, we make the summary uppercase.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example()  # open a calendar
    >>> find_christmas = lambda c: "christmas" in  c.get("SUMMARY", "").lower()
    >>> for component in calendar.walk(select=find_christmas):
    ...     component["SUMMARY"] = component["SUMMARY"].upper()
    >>> print(calendar.events[1].summary)
    ORTHODOX CHRISTMAS
