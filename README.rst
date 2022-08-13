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

.. image:: https://github.com/collective/icalendar/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/collective/icalendar/actions/workflows/tests.yml
    :alt: GitHub Actions build status for master

.. image:: https://github.com/collective/icalendar/actions/workflows/tests.yml/badge.svg?branch=4.x
    :target: https://github.com/collective/icalendar/actions/workflows/tests.yml
    :alt: GitHub Actions build status for 4.x

.. _`icalendar`: https://pypi.org/project/icalendar/
.. _`RFC 5545`: https://www.ietf.org/rfc/rfc5545.txt
.. _`python-dateutil`: https://github.com/dateutil/dateutil/
.. _`pytz`: https://pypi.org/project/pytz/
.. _`BSD`: https://github.com/collective/icalendar/issues/2


Related projects
================

* `icalevents <https://github.com/irgangla/icalevents>`_. It is built on top of icalendar and allows you to query iCal files and get the events happening on specific dates. It manages recurrent events as well.
* `recurring-ical-events <https://pypi.org/project/recurring-ical-events/>`_. Library to query an ``ICalendar`` object for events happening at a certain date or within a certain time.
* `x-wr-timezone <https://pypi.org/project/x-wr-timezone/>`_. Library to make ``ICalendar`` objects and files using the non-standard ``X-WR-TIMEZONE`` compliant with the standard (RFC 5545).
