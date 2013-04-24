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
    :Compatible with: Python 2.6 and 2.7
    :License: `BSD`_

----


Changes in version 3.0
======================

API Change
----------

Since version we unified to icalendar de/serialization API to use only to_ical
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

Instead of the own UTC tzinfo implementation we use pytz UTC tzinfo object now.


Roadmap
=======

1) Internally Unicode will be used exclusively.

2) On API Functions, accept or return Unicode or en/decoded strings.

3) This will make the 3.4 Release.

4) API change: API calls also only accept/return Unicode.

5) This will make the 4.0 release.



About this fork which is not a fork anymore
===========================================

Aim of this fork (not fork anymore, read further) was to bring this package up
to date with latest icalendar `RFC`_ specification as part of
`plone.app.event`_ project which goal is to bring recurrent evens to `Plone`_.

After some thoughts we (Plone developers involved with `plone.app.event`_) send
a suggestion to icalendar-dev@codespeak.net to take over mainaining of
`icalendar`_. Nobody object and since version 2.2 we are back to development.

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

    Name                                                           Stmts   Miss  Cover
    ----------------------------------------------------------------------------------
    .tox/py27/lib/python2.7/site-packages/icalendar/__init__           6      0   100%
    .tox/py27/lib/python2.7/site-packages/icalendar/cal              223      8    96%
    .tox/py27/lib/python2.7/site-packages/icalendar/caselessdict      55      2    96%
    .tox/py27/lib/python2.7/site-packages/icalendar/parser           181     18    90%
    .tox/py27/lib/python2.7/site-packages/icalendar/parser_tools      19      0   100%
    .tox/py27/lib/python2.7/site-packages/icalendar/prop             521     59    89%
    .tox/py27/lib/python2.7/site-packages/icalendar/tools             12      0   100%
    ----------------------------------------------------------------------------------
    TOTAL                                                           1017     87    91%
