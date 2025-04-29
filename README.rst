==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar`_ package is a :rfc:`5545` compatible parser/generator for iCalendar
files.

----

:Homepage: https://icalendar.readthedocs.io
:Community Discussions: https://github.com/collective/icalendar/discussions
:Issue Tracker: https://github.com/collective/icalendar/issues
:Code: https://github.com/collective/icalendar
:Dependencies: `python-dateutil`_ and `tzdata`_.
:License: `BSD`_

----

.. image:: https://badge.fury.io/py/icalendar.svg
   :target: https://pypi.org/project/icalendar/
   :alt: Python Package Version on PyPI

.. image:: https://img.shields.io/pypi/pyversions/icalendar
   :target: https://pypi.org/project/icalendar/
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/dm/icalendar.svg
   :target: https://pypi.org/project/icalendar/#files
   :alt: Downloads from PyPI

.. image:: https://img.shields.io/github/actions/workflow/status/collective/icalendar/tests.yml?branch=main&label=main&logo=github
    :target: https://github.com/collective/icalendar/actions/workflows/tests.yml?query=branch%3Amain
    :alt: GitHub Actions build status for main

.. image:: https://readthedocs.org/projects/icalendar/badge/?version=latest
    :target: https://icalendar.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/collective/icalendar/badge.svg
    :target: https://coveralls.io/github/collective/icalendar
    :alt: Test Coverage


.. _`icalendar`: https://pypi.org/project/icalendar/
.. _`python-dateutil`: https://github.com/dateutil/dateutil/
.. _`tzdata`: https://pypi.org/project/tzdata/
.. _`BSD`: https://github.com/collective/icalendar/issues/2

Quick start guide
=================

``icalendar`` enables you to **create**, **inspect** and **modify**
calendaring information with Python.

To **install** the package, run::

    pip install icalendar


Inspect Files
-------------

You can open an ``.ics`` file and see all the events:

.. code:: python

  >>> import icalendar
  >>> from pathlib import Path
  >>> ics_path = Path("src/icalendar/tests/calendars/example.ics")
  >>> calendar = icalendar.Calendar.from_ical(ics_path.read_bytes())
  >>> for event in calendar.events:
  ...     print(event.get("SUMMARY"))
  New Year's Day
  Orthodox Christmas
  International Women's Day

Modify Content
--------------

Such a calendar can then be edited and saved again.

.. code:: python

    >>> calendar["X-WR-CALNAME"] = "My Modified Calendar"  # modify
    >>> print(calendar.to_ical()[:129])  # save modification
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:collective/icalendar
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    X-WR-CALNAME:My Modified Calendar


Create Events, TODOs, Journals, Alarms, ...
-------------------------------------------

``icalendar`` supports the creation and parsing of all kinds of objects
in the iCalendar (:rfc:`5545`) standard.

.. code:: python

    >>> icalendar.Event()  # events
    VEVENT({})
    >>> icalendar.FreeBusy()  # free/busy times
    VFREEBUSY({})
    >>> icalendar.Todo()  # Todo list entries
    VTODO({})
    >>> icalendar.Alarm()  # Alarms e.g. for events
    VALARM({})
    >>> icalendar.Journal()   # Journal entries
    VJOURNAL({})


Have a look at `more examples
<https://icalendar.readthedocs.io/en/latest/usage.html>`_.

Use timezones of your choice
----------------------------

With ``icalendar``, you can localize your events to take place in different
timezones.
``zoneinfo``, ``dateutil.tz`` and ``pytz`` are compatible with ``icalendar``.
This example creates an event that uses all of the timezone implementations
with the same result:

.. code:: python

    >>> import pytz, zoneinfo, dateutil.tz  # timezone libraries
    >>> import datetime, icalendar
    >>> e = icalendar.Event()
    >>> tz = dateutil.tz.tzstr("Europe/London")
    >>> e["X-DT-DATEUTIL"] = icalendar.vDatetime(datetime.datetime(2024, 6, 19, 10, 1, tzinfo=tz))
    >>> tz = pytz.timezone("Europe/London")
    >>> e["X-DT-USE-PYTZ"] = icalendar.vDatetime(datetime.datetime(2024, 6, 19, 10, 1, tzinfo=tz))
    >>> tz = zoneinfo.ZoneInfo("Europe/London")
    >>> e["X-DT-ZONEINFO"] = icalendar.vDatetime(datetime.datetime(2024, 6, 19, 10, 1, tzinfo=tz))
    >>> print(e.to_ical())  # the libraries yield the same result
    BEGIN:VEVENT
    X-DT-DATEUTIL;TZID=Europe/London:20240619T100100
    X-DT-USE-PYTZ;TZID=Europe/London:20240619T100100
    X-DT-ZONEINFO;TZID=Europe/London:20240619T100100
    END:VEVENT

Version 6 with zoneinfo
-----------------------

Version 6 of ``icalendar`` switches the timezone implementation to ``zoneinfo``.
This only affects you if you parse ``icalendar`` objects with ``from_ical()``.
The functionality is extended and is tested since 6.0.0 with both timezone
implementations ``pytz`` and ``zoneinfo``.

By default and since 6.0.0, ``zoneinfo`` timezones are created.

.. code:: python

    >>> dt = icalendar.Calendar.example("timezoned").events[0].start
    >>> dt.tzinfo
    ZoneInfo(key='Europe/Vienna')

If you would like to continue to receive ``pytz`` timezones in parse results,
you can receive all the latest updates, and switch back to earlier behavior:

.. code:: python

    >>> icalendar.use_pytz()
    >>> dt = icalendar.Calendar.example("timezoned").events[0].start
    >>> dt.tzinfo
    <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>

Version 6 is on `branch main <https://github.com/collective/icalendar/>`_.
It is compatible with Python versions 3.8 - 3.13, and PyPy3.
We expect the ``main`` branch with versions ``6+`` to receive the latest updates and features.

Related projects
================

* `icalevents <https://github.com/irgangla/icalevents>`_. It is built on top of icalendar and allows you to query iCal files and get the events happening on specific dates. It manages recurrent events as well.
* `recurring-ical-events <https://pypi.org/project/recurring-ical-events/>`_. Library to query an ``icalendar.Calendar`` object for events and other components happening at a certain date or within a certain time.
* `x-wr-timezone <https://pypi.org/project/x-wr-timezone/>`_. Library and command line tool to make ``icalendar.Calendar`` objects and files from Google Calendar (using the non-standard ``X-WR-TIMEZONE`` property) compliant with the standard (:rfc:`5545`).
* `ics-query <http://pypi.org/project/ics-query>`_. Command line tool to query iCalendar files for occurrences of events and other components.
* `icalendar-compatibility <https://icalendar-compatibility.readthedocs.io/en/latest/>`_ - access to event data compatible with RFC5545 and different implementations

Further Reading
===============

You can find out more about this project:

* `Contributing`_
* `Changelog`_
* `License`_

.. _`Contributing`: https://icalendar.readthedocs.io/en/latest/contributing.html
.. _`Changelog`: https://icalendar.readthedocs.io/en/latest/changelog.html
.. _`License`: https://icalendar.readthedocs.io/en/latest/license.html
