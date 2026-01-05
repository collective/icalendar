==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar <https://pypi.org/project/icalendar/>`_ package is an :rfc:`5545` compatible parser and generator of iCalendar files.

icalendar can create, inspect, and modify calendaring information with Python.

icalendar supports multiple timezone implementations, including `zoneinfo <https://docs.python.org/3/library/zoneinfo.html>`_, `dateutil.tz <https://dateutil.readthedocs.io/en/latest/tz.html>`_, and `pytz <https://pypi.org/project/pytz/>`_.


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
