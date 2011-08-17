==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar`_ package is a parser/generator of iCalendar files for use
with Python.


About this fork
===============

.. warning::

    This part should be removed actual before release.

Aim of this fork is to bring this package up to date with latest RFC
specification as part of `plone.app.event`_ project which aims is to bring
recurrence evens to `Plone`_.

Current plan:

    1. Merge bugfixes from forks listed bellow.
    2. Contact all interested and try to get release 2.2 out.
    3. Start working on 3.0 to bring package up-to-date with newer iCalendar
       specification (`RFC 5545`_), while keeping 2.X series to be backwords
       compatible with `RFC 2445`_.

Known forks:

 - https://codespeak.net/svn/iCalendar/trunk/
   The original codespeak repo, which this branch is based on (keeping it up to
   date in ``svn-trunk`` branch)

 - https://github.com/cozi/icalendar
   The icalendar fork of the Cozi group with many fixes and additions. 
   Especially ``master-future`` branch is interesting.

 - https://github.com/greut/iCalendar
   Another repository. All changes except the one from commit
   #5166fa914593d8366044 were integrated into the cozi fork.

 - https://github.com/ryba-xek/iCalendar
   Another repo which fixes an Unicode issue with folding. Integrated into
   cozi.

 - https://github.com/1calendar/icalendar
   Same as above.

 - https://bitbucket.org/psagers/icalendar
   Another repo which fixes something also integrated in greut's repo, but not
   in cozi's. Not sure if we need it.


.. _`icalendar`: http://pypi.python.org/pypi/icalendar
.. _`plone.app.event`: http://github.com/collective/plone.app.event
.. _`Plone`: http://plone.org
.. _`RFC 5545`: http://www.ietf.org/rfc/rfc5545.txt
.. _`RFC 2445`: http://www.ietf.org/rfc/rfc2445.txt



.. warning::

    Below is content of previous README.



Introduction
============

I (Max M) have often needed to parse and generate iCalendar
files. Finally I got tired of writing ad-hoc tools.

So this is my attempt at making an iCalendar package for Python. The
inspiration has come from the email package in the standard lib, which
I think is pretty simple, yet efficient and powerful.

The package can both generate and parse iCalendar files, and can
easily be used as is.

The aim is to make a package that is fully compliant to RFC 2445, well
designed, simple to use and well documented.

News
====

* 2008-07-11: `iCalendar 2.0`_ released (`changes for 2.0`_)
* 2006-11-26: `iCalendar 1.2`_ released (`changes for 1.2`_)
* 2006-11-23: `iCalendar 1.1`_ released (`changes for 1.1`_)
* 2006-08-03: `iCalendar 1.0`_ released (`changes for 1.0`_)
* 2005-11-08: `iCalendar 0.11`_ released (`changes for 0.11`_)
* 2005-04-28: `iCalendar 0.10`_ released (`changes for 0.10`_)

.. _`iCalendar 2.0`: iCalendar-2.0.tgz
.. _`changes for 2.0`: changes-2.0.html
.. _`iCalendar 1.2`: iCalendar-1.2.tgz
.. _`changes for 1.2`: changes-1.2.html
.. _`iCalendar 1.1`: iCalendar-1.1.tgz
.. _`changes for 1.1`: changes-1.1.html
.. _`iCalendar 1.0`: iCalendar-1.0.tgz
.. _`changes for 1.0`: changes-1.0.html
.. _`iCalendar 0.11`: iCalendar-0.11.tgz
.. _`changes for 0.11`: changes-0.11.html
.. _`iCalendar 0.10`: iCalendar-0.10.tgz
.. _`changes for 0.10`: changes-0.10.html

Example
=======

To open and parse a file::

  >>> from icalendar import Calendar, Event
  >>> cal = Calendar.from_string(open('test.ics','rb').read())
  >>> cal
  VCALENDAR({'VERSION': vText(u'2.0'), 'METHOD': vText(u'Request'), 'PRODID': vText(u'-//My product//mxm.dk/')})

  >>> for component in cal.walk():
  ...     component.name
  'VCALENDAR'
  'VEVENT'
  'VEVENT'

To create a calendar and write it to disk::

  >>> cal = Calendar()
  >>> from datetime import datetime
  >>> from icalendar import UTC # timezone
  >>> cal.add('prodid', '-//My calendar product//mxm.dk//')
  >>> cal.add('version', '2.0')

  >>> event = Event()
  >>> event.add('summary', 'Python meeting about calendaring')
  >>> event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=UTC))
  >>> event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=UTC))
  >>> event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC))
  >>> event['uid'] = '20050115T101010/27346262376@mxm.dk'
  >>> event.add('priority', 5)

  >>> cal.add_component(event)

  >>> f = open('example.ics', 'wb')
  >>> f.write(cal.as_string())
  >>> f.close()

More documentation
==================

Consult this example_ for introductory doctests and explanations. Here
are two smaller_ examples_.

.. _example: example.html
.. _smaller: small.html
.. _examples: groupscheduled.html
.. _multiple: multiple.html

All modules and classes also have doctests that shows how they
work. There is also an `interfaces.py`_ file which describes the API.

.. _`interfaces.py`: interfaces.py

Mailing list
============

If you have any comments or feedback on the module, please use the iCalendar
mailing list. You can subscribe to it here:

http://codespeak.net/mailman/listinfo/icalendar-dev

We would love to hear use cases, or get ideas for improvements.

There is also a checkins mailing list, if you want to follow development:

http://codespeak.net/mailman/listinfo/icalendar-checkins

Download
========

* `iCalendar 2.0`_ (2008-07-11)
* `iCalendar 1.2`_ (2006-11-26)
* `iCalendar 1.1`_ (2006-11-23)
* `iCalendar 1.0`_ (2006-08-03)
* `iCalendar 0.11`_ (2005-08-11)
* `iCalendar 0.10`_ (2005-04-28)

You can also check out the `development version of iCalendar`_ from
subversion, using a command like::

  svn co http://codespeak.net/svn/iCalendar/trunk iCalendar

.. _`development version of iCalendar`: http://codespeak.net/svn/iCalendar/trunk

Dependencies
============

It is dependent on the datetime package, so it requires Python >=
2.3. There are no other dependencies.

License
=======

LGPL. See LICENSE.txt for details.
