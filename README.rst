==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar <https://pypi.org/project/icalendar/>`_ package is an :rfc:`5545` compatible parser and generator of iCalendar files.

icalendar can create, inspect, and modify calendaring information with Python.

----

:Homepage: https://icalendar.readthedocs.io/en/stable/
:Community Discussions: https://github.com/collective/icalendar/discussions
:Issue Tracker: https://github.com/collective/icalendar/issues
:Code: https://github.com/collective/icalendar
:Dependencies: `python-dateutil <https://pypi.org/project/python-dateutil/>`_ and `tzdata <https://pypi.org/project/tzdata/>`_.
:License: `2-Clause BSD License <https://github.com/collective/icalendar/blob/main/LICENSE.rst>`_
:Contribute: `Contribute to icalendar <https://icalendar.readthedocs.io/en/latest/contribute/index.html>`_
:Funding: `Open Collective <https://opencollective.com/python-icalendar>`_

----

.. image:: https://img.shields.io/pypi/v/icalendar
    :target: https://pypi.org/project/icalendar/
    :alt: Python package version on PyPI

.. image:: https://img.shields.io/github/v/release/collective/icalendar
    :target: https://pypi.org/project/icalendar/#history
    :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/icalendar
    :target: https://pypi.org/project/icalendar/
    :alt: Supported Python versions

.. image:: https://static.pepy.tech/personalized-badge/icalendar?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=downloads
    :target: https://pypistats.org/packages/icalendar
    :alt: Downloads from PyPI

.. image:: https://img.shields.io/github/actions/workflow/status/collective/icalendar/tests.yml?branch=main&label=main&logo=github
    :target: https://github.com/collective/icalendar/actions/workflows/tests.yml?query=branch%3Amain
    :alt: GitHub Actions build status for main

.. image:: https://readthedocs.org/projects/icalendar/badge/?version=latest
    :target: https://icalendar.readthedocs.io/en/latest/
    :alt: Documentation status

.. image:: https://coveralls.io/repos/github/collective/icalendar/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/icalendar?branch=main
    :alt: Test coverage

.. image:: https://img.shields.io/badge/%F0%9F%A4%91-Funding-brightgreen
    :target: https://opencollective.com/python-icalendar
    :alt: Funding


Install icalendar
=================

See how to `install icalendar <https://icalendar.readthedocs.io/en/stable/install.html>`_.


Usage
=====

For how to use icalendar, including how to read, modify, and write iCalendar files, see the `Usage <https://icalendar.readthedocs.io/en/latest/how-to/usage.html>`_ guide.


Modify Content
--------------

Such a calendar can then be edited and saved again.

.. code:: python

    >>> calendar.calendar_name = "My Modified Calendar"  # modify
    >>> print(calendar.to_ical()[:121])  # save modification
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:collective/icalendar
    CALSCALE:GREGORIAN
    METHOD:PUBLISH
    NAME:My Modified Calendar


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
<https://icalendar.readthedocs.io/en/latest/how-to/usage.html>`_.

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

* `vobject <https://github.com/py-vobject/vobject>`_ is a different Python library for iCalendar.
* `icalevents <https://github.com/irgangla/icalevents>`_. It is built on top of icalendar and allows you to query iCal files and get the events happening on specific dates. It manages recurrent events as well.
* `recurring-ical-events <https://pypi.org/project/recurring-ical-events/>`_. Library to query an ``icalendar.Calendar`` object for events and other components happening at a certain date or within a certain time.
* `x-wr-timezone <https://pypi.org/project/x-wr-timezone/>`_. Library and command line tool to make ``icalendar.Calendar`` objects and files from Google Calendar (using the non-standard ``X-WR-TIMEZONE`` property) compliant with the standard (:rfc:`5545`).
* `ics-query <http://pypi.org/project/ics-query>`_. Command line tool to query iCalendar files for occurrences of events and other components.
* `icalendar-compatibility <https://icalendar-compatibility.readthedocs.io/en/latest/>`_ - access to event data compatible with RFC5545 and different implementations
* `caldav <https://caldav.readthedocs.io/>`_ is based on ``icalendar``.
* `icalendar-anonymizer <https://pypi.org/project/icalendar-anonymizer/>`_ is a tool to anonymize ical files so they can be published or shared for debugging and other purposes without revealing personal information.


Change log
==========

See the `change log <https://icalendar.readthedocs.io/en/latest/reference/changelog.html>`_ for the latest updates to icalendar.
