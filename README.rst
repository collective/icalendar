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

To **install** the package, run::

    pip install icalendar

You can open an ``.ics`` file and see all the events::

  >>> import icalendar
  >>> path_to_ics_file = "src/icalendar/tests/calendars/example.ics"
  >>> with open(path_to_ics_file) as f:
  ...     calendar = icalendar.Calendar.from_ical(f.read())
  >>> for event in calendar.walk('VEVENT'):
  ...     print(event.get("SUMMARY"))
  New Year's Day
  Orthodox Christmas
  International Women's Day

Using this package, you can also create calendars from scratch or edit existing ones.

Versions and Compatibility
--------------------------

``icalendar`` is a critical project used by many. It has been there for a long time and maintaining
long-term compatibility with projects conflicts partially with providing and using the features that
the latest Python versions bring.

Since we pour more `effort into maintaining and developing icalendar <https://github.com/collective/icalendar/discussions/360>`__,
we split the project into two:

- `Branch 4.x <https://github.com/collective/icalendar/tree/4.x>`__ with maximum compatibility to Python versions ``2.7`` and ``3.4+``, ``PyPy2`` and ``PyPy3``.
- `Branch master <https://github.com/collective/icalendar/>`__ with the compatibility to Python versions ``3.7+`` and ``PyPy3``.

We expect the ``master`` branch with versions ``5+`` receive the latest updates and features,
and the ``4.x`` branch the subset of security and bug fixes only.
We recommend migrating to later Python versions and also providing feedback if you depend on the ``4.x`` features.

Related projects
================

* `icalevents <https://github.com/irgangla/icalevents>`_. It is built on top of icalendar and allows you to query iCal files and get the events happening on specific dates. It manages recurrent events as well.
* `recurring-ical-events <https://pypi.org/project/recurring-ical-events/>`_. Library to query an ``ICalendar`` object for events happening at a certain date or within a certain time.
* `x-wr-timezone <https://pypi.org/project/x-wr-timezone/>`_. Library to make ``ICalendar`` objects and files using the non-standard ``X-WR-TIMEZONE`` compliant with the standard (RFC 5545).
