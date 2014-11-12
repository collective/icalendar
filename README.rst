==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar`_ package is a parser/generator of iCalendar files for use
with Python.

----

    :Homepage: http://icalendar.readthedocs.org
    :Code: http://github.com/collective/icalendar
    :Mailing list: http://github.com/collective/icalendar/issues
    :Dependencies: `setuptools`_ and since version 3.0 we depend on `pytz`_.
    :Compatible with: Python 2.6, 2.7 and 3.3+
    :License: `BSD`_

----


.. image:: https://travis-ci.org/collective/icalendar.svg?branch=master
    :target: https://travis-ci.org/collective/icalendar


Roadmap
=======

- 4.0: API refactoring



Changes in version 3.0
======================

API Change
----------

Since version 3.0 the icalendar de/serialization API is unified to use only to_ical
(for writing an ical string from the internal representation) and from_ical
(for parsing an ical string into the internal representation).

to_ical is now used instead of the methods ical, string, as_string and instead
of string casting via __str__ and str.

from_ical is now used instead of from_string.

This change is a requirement for future Python 3 compatibility. Please update
your code to reflect to the new API.

Timezone support
----------------

Timezones are now fully supported in icalendar for serialization and
deserialization. We use the pytz library for timezone components of datetime
instances. The timezone identifiers must be valid pytz respectively Olson
database timezone identifiers. This can be a problem for 'GMT' identifiers,
which are not defined in the Olson database.

Instead of our own UTC tzinfo implementation we use pytz UTC tzinfo object now.


About this fork which is not a fork anymore
===========================================

The aim of this fork (not fork anymore, read further) was to bring this package
up to date with latest icalendar `RFC`_ specification as part of
`plone.app.event`_ project which goal is to bring recurrent events to `Plone`_.

After some thoughts we (Plone developers involved with `plone.app.event`_) send
a suggestion to icalendar-dev@codespeak.net to take over maintaining of
`icalendar`_. Nobody objected and since version 2.2 we are back to development.

.. _`icalendar`: http://pypi.python.org/pypi/icalendar
.. _`plone.app.event`: http://github.com/plone/plone.app.event
.. _`Plone`: http://plone.org
.. _`pytz`: http://pypi.python.org/pypi/pytz
.. _`setuptools`: http://pypi.python.org/pypi/setuptools
.. _`RFC`: http://www.ietf.org/rfc/rfc5545.txt
.. _`BSD`: https://github.com/collective/icalendar/issues/2


Test Coverage Report
====================

Output from coverage test::

    Name                         Stmts   Miss  Cover
    ------------------------------------------------
    src/icalendar/__init__           4      0   100%
    src/icalendar/cal              243      7    97%
    src/icalendar/caselessdict      66      7    89%
    src/icalendar/compat             1      0   100%
    src/icalendar/parser           192      6    97%
    src/icalendar/parser_tools      20      0   100%
    src/icalendar/prop             536     64    88%
    src/icalendar/tools             16      0   100%
    ------------------------------------------------
    TOTAL                         1078     84    92%
