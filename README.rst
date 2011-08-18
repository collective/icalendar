==========================================================
Internet Calendaring and Scheduling (iCalendar) for Python
==========================================================

The `icalendar`_ package is a parser/generator of iCalendar files for use
with Python.

----

    :Code: http://github.com/collective/icalendar
    :Mailing list: http://codespeak.net/mailman/listinfo/icalendar-dev
    :Dependencies: There are no other dependencies.
    :Tested with: Python 2.4 - 2.7
    :License: ???

----

About this fork
===============

.. warning::

    This part should be removed actual before release.

Aim of this fork is to bring this package up to date with latest RFC
specification as part of `plone.app.event`_ project which aims is to bring
recurrence evens to `Plone`_.

Current plan
------------

    1. Merge bugfixes from forks listed bellow.
    2. Contact all interested and try to get release 2.2 out.
    3. Start working on 3.0 to bring package up-to-date with newer iCalendar
       specification (`RFC 5545`_), while keeping 2.X series compatible with
       `RFC 2445`_.

Known forks
-----------

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


Todo
----

 - license: there is a little bit of mess with licensing. it would be good
   contact all contributors and ask them to change to one license (maybe
   propose BSD)? more about it here:
   http://codespeak.net/pipermail/icalendar-dev/2010-August/000157.html
 - mailing list: should we move mailing list from codespeak, since its services
   are shuting down? 


.. _`icalendar`: http://pypi.python.org/pypi/icalendar
.. _`plone.app.event`: http://github.com/collective/plone.app.event
.. _`Plone`: http://plone.org
.. _`RFC 5545`: http://www.ietf.org/rfc/rfc5545.txt
.. _`RFC 2445`: http://www.ietf.org/rfc/rfc2445.txt
