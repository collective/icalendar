==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar`_ package is a `RFC 5545`_ compatible parser/generator for iCalendar
files.

----

:Homepage: https://icalendar.readthedocs.io
:Code: https://github.com/collective/icalendar
:Mailing list: https://github.com/collective/icalendar/issues
:Dependencies: `python-dateutil`_ and `pytz`_.
:Compatible with: Python 2.7 and 3.4+
:License: `BSD`_

----

.. image:: https://badge.fury.io/py/icalendar.svg
   :target: https://pypi.org/project/icalendar/
   :alt: Python Package Version on PyPI

.. image:: https://img.shields.io/pypi/dm/icalendar.svg
   :target: https://pypi.org/project/icalendar/#files
   :alt: Downloads from PyPI

.. image:: https://img.shields.io/github/actions/workflow/status/collective/icalendar/tests.yml?branch=master&label=master&logo=github
    :target: https://github.com/collective/icalendar/actions/workflows/tests.yml?query=branch%3Amaster
    :alt: GitHub Actions build status for master

.. image:: https://img.shields.io/github/actions/workflow/status/collective/icalendar/tests.yml?branch=4.x&label=4.x&logo=github
    :target: https://github.com/collective/icalendar/actions/workflows/tests.yml?query=branch%3A4.x++
    :alt: GitHub Actions build status for 4.x

.. image:: https://readthedocs.org/projects/icalendar/badge/?version=latest
    :target: https://icalendar.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. _`icalendar`: https://pypi.org/project/icalendar/
.. _`RFC 5545`: https://www.ietf.org/rfc/rfc5545.txt
.. _`python-dateutil`: https://github.com/dateutil/dateutil/
.. _`pytz`: https://pypi.org/project/pytz/
.. _`BSD`: https://github.com/collective/icalendar/issues/2

Quick Guide
-----------

``icalendar`` enables you to **create**, **inspect** and **modify**
calendaring information with Python.

To **install** the package, run::

    pip install icalendar


Inspect Files
~~~~~~~~~~~~~

You can open an ``.ics`` file and see all the events::

  >>> import icalendar
  >>> from pathlib import Path
  >>> ics_path = Path("src/icalendar/tests/calendars/example.ics")
  >>> with ics_path.open() as f:
  ...     calendar = icalendar.Calendar.from_ical(f.read())
  >>> for event in calendar.walk('VEVENT'):
  ...     print(event.get("SUMMARY"))
  New Year's Day
  Orthodox Christmas
  International Women's Day

Modify Content
~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``icalendar`` supports the creation and parsing of all kinds of objects
in the iCalendar (RFC 5545) standard.

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

Use Timezones of your choice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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



Versions and Compatibility
--------------------------

``icalendar`` is a critical project used by many. It has been there for a long time and maintaining
long-term compatibility with projects conflicts partially with providing and using the features that
the latest Python versions bring.

Volunteers pour `effort into maintaining and developing icalendar
<https://github.com/collective/icalendar/discussions/360>`__.
Below, you can find an overview of the versions and how we maintain them.

Version 6
~~~~~~~~~

Version 6 of ``icalendar`` switches the timezone implementation to ``zoneinfo``.
This only affects you if you parse ``icalendar`` objects with ``from_ical()``.
The functionality is extended and is tested since 6.0.0 with both timezone
implementations: ``pytz`` and ``zoneinfo``.

By default and since 6.0.0, ``zoneinfo`` timezones are created.

.. code:: python

    >>> dt = icalendar.Calendar.example("timezoned").walk("VEVENT")[0]["DTSTART"].dt
    >>> dt.tzinfo
    ZoneInfo(key='Europe/Vienna')

If you would like to continue to receive ``pytz`` timezones in as parse results,
you can receive all the latest updates, and switch back to version 5.x behavior:

.. code:: python

    >>> icalendar.use_pytz()
    >>> dt = icalendar.Calendar.example("timezoned").walk("VEVENT")[0]["DTSTART"].dt
    >>> dt.tzinfo
    <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>

Version 6 is on `branch master <https://github.com/collective/icalendar/>`_ with compatibility to Python versions ``3.7+`` and ``PyPy3``.
We expect the ``master`` branch with versions ``6+`` to receive the latest updates and features.

Version 5
~~~~~~~~~

Version 5 uses only the ``pytz`` timezone implementation, and not ``zoneinfo``.
No updates will be released for this.
Please use version 6 and switch to use ``zoneinfo`` as documented above.

Version 4
~~~~~~~~~

Version 4 is on `branch 4.x <https://github.com/collective/icalendar/tree/4.x>`_ with maximum compatibility with Python versions ``2.7`` and ``3.4+``, ``PyPy2`` and ``PyPy3``.
The ``4.x`` branch only receives security and bug fixes if someone makes the effort.
We recommend migrating to later Python versions and also providing feedback if you depend on the ``4.x`` features.

Related projects
================

* `icalevents <https://github.com/irgangla/icalevents>`_. It is built on top of icalendar and allows you to query iCal files and get the events happening on specific dates. It manages recurrent events as well.
* `recurring-ical-events <https://pypi.org/project/recurring-ical-events/>`_. Library to query an ``ICalendar`` object for events happening at a certain date or within a certain time.
* `x-wr-timezone <https://pypi.org/project/x-wr-timezone/>`_. Library to make ``ICalendar`` objects and files using the non-standard ``X-WR-TIMEZONE`` compliant with the standard (RFC 5545).
