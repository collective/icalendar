Miscellaneous examples
======================

This section describes how to solve specific usage issues with icalendar.
Post your usage question to the `icalendar discussion Q&A category <https://github.com/collective/icalendar/discussions/categories/q-a>`_.
You may :doc:`contribute answered questions to this section of the documentation <../contribute/documentation/index>` through a pull request, too.

Convert iCalendar to JSON
=========================

See the :doc:`jcal` documentation for how to convert iCalendar data to JSON.

Print event information
=======================

To print all events of an iCalendar, iterate through them and print each as shown.

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

Modify specific events
======================

To find :attr:`~icalendar.cal.component.Component.subcomponents` that match specific requirements, use :meth:`~icalendar.cal.component.Component.walk`.

The following example filters through all subcomponents of the calendar, and if they have a specific word ``Christmas`` in their summary, makes the summary uppercase.

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example()  # open a calendar
    >>> find_christmas = lambda c: "christmas" in  c.get("SUMMARY", "").lower()
    >>> for component in calendar.walk(select=find_christmas):
    ...     component["SUMMARY"] = component["SUMMARY"].upper()
    >>> print(calendar.events[1].summary)
    ORTHODOX CHRISTMAS

Add timezones to a calendar
===========================

Dates with times in icalendar can be timezone specific.
``UTC`` is such a timezone.
Other examples are ``Europe/Berlin``, ``America/New_York``, and ``Asia/Tokyo``.

The following example creates a calendar with an event in ``Europe/Zurich``, and adds all needed timezones just before saving the calendar.

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