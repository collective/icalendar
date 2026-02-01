==========
How do I …
==========

This document collects questions and their answers about how to solve a specific problem with icalendar.
If you have a question on how to solve a specific problem with icalendar, please post it on the `icalendar forum <https://github.com/collective/icalendar/discussions/categories/q-a>`_.

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

… add timezones to a calendar?
==============================

Dates with times in icalendar can be timezone specific.
``UTC`` is such a timezone. Other examples are ``Europe/Berlin``, ``America/New_York``, and ``Asia/Tokyo``.

In this example, we create a calendar with an event happening in ``Europe/Zurich`` and add all needed timezones just before saving the calendar.

.. code-block:: pycon

    >>> from icalendar import Calendar, Event
    >>> from datetime import datetime
    >>> from zoneinfo import ZoneInfo
    >>> event = Event.new(
    ...     summary="Meeting in Zurich",
    ...     start=datetime(2022, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Europe/Zurich")),
    ...     end=datetime(2022, 1, 1, 13, 0, 0, tzinfo=ZoneInfo("Europe/Zurich")),
    ...     location="Zurich, Switzerland",
    ... )
    >>> calendar = Calendar.new(
    ...     subcomponents=[event],    
    ... )
    >>> calendar.add_missing_timezones()
    >>> 'Europe/Zurich' in [tz.tz_name for tz in calendar.timezones]
    True

After running :meth:`~icalendar.cal.calendar.Calendar.add_missing_timezones`, the calendar now contains all needed timezones and can be saved as a file with :meth:`~icalendar.cal.component.Component.to_ical`.