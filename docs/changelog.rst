Changelog
=========


3.0.1b1 (2012-02-24)
------------------

* Update Release information.
  [thet]

3.0
---

* Add API for proper Timezone support. Allow creating ical DATE-TIME strings
  with timezone information from Python datetimes with pytz based timezone
  information and vice versa.
  [thet]

* Unify API to only use to_ical and from_ical and remove any __str__ API
  definitions. This is one requirement for Python 3 compatibility.
  [thet]

2.2 (2011-08-24)
----------------

* migration to https://github.com/collective/icalendar using svn2git preserving
  tags, branches and authors.
  [garbas]

* using tox for testing on python 2.4, 2.5, 2.6, 2.6.
  [garbas]

* fixed tests so they pass also under python 2.7.
  [garbas]

* running tests on https://jenkins.plone.org/job/icalendar (only 2.6 for now)
  with some other metrics (pylint, clonedigger, coverage).
  [garbas]

* review and merge changes from https://github.com/cozi/icalendar fork.
  [garbas]

* created sphinx documentation and started documenting development and goals.
  [garbas]

* hook out github repository to http://readthedocs.org service so sphinx
  documentation is generated on each commit (for master). Documentation can be
  visible on: http://readthedocs.org/docs/icalendar/en/latest/
  [garbas]


2.1 (2009-12-14)
----------------

* Fix deprecation warnings about ``object.__init__`` taking no parameters.

* Set the VALUE parameter correctly for date values.

* Long binary data would be base64 encoded with newlines, which made the
  iCalendar files incorrect. (This still needs testing).

* Correctly handle content lines which include newlines.


2.0.1 (2008-07-11)
------------------

* Made the tests run under Python 2.5+

* Renamed the UTC class to Utc, so it would not clash with the UTC object,
  since that rendered the UTC object unpicklable.  


2.0 (2008-07-11)
----------------

* EXDATE and RDATE now returns a vDDDLists object, which contains a list
  of vDDDTypes objects. This is do that EXDATE and RDATE can contain
  lists of dates, as per RFC.
  
  ***Note!***: This change is incompatible with earlier behavior, so if you
  handle EXDATE and RDATE you will need to update your code.

* When createing a vDuration of -5 hours (which in itself is nonsensical),
  the ical output of that was -P1DT19H, which is correct, but ugly. Now
  it's '-PT5H', which is prettier.


1.2 (2006-11-25)
----------------

* Fixed a string index out of range error in the new folding code.


1.1 (2006-11-23)
----------------

* Fixed a bug in caselessdicts popitem. (thanks to Michael Smith
  <msmith@fluendo.com>)

* The RFC 2445 was a bit unclear on how to handle line folding when it
  happened to be in the middle of a UTF-8 character. This has been clarified
  in the following discussion: http://lists.osafoundation.org/pipermail/ietf-calsify/2006-August/001126.html
  And this is now implemented in iCalendar. It will not fold in the middle of
  a UTF-8 character, but may fold in the middle of a UTF-8 composing character
  sequence.


1.0 (2006-08-03)
----------------

* make get_inline and set_inline support non ascii codes.

* Added support for creating a python egg distribution.


0.11 (2005-11-08)
-----------------

* Changed component .from_string to use types_factory instead of hardcoding
  entries to 'inline'

* Changed UTC tzinfo to a singleton so the same one is used everywhere

* Made the parser more strict by using regular expressions for key name,
  param name and quoted/unquoted safe char as per the RFC

* Added some tests from the schooltool icalendar parser for better coverage

* Be more forgiving on the regex for folding lines

* Allow for multiple top-level components on .from_string

* Fix vWeekdays, wasn't accepting relative param (eg: -3SA vs -SA)

* vDDDTypes didn't accept negative period (eg: -P30M)

* 'N' is also acceptable as newline on content lines, per RFC


0.10 (2005-04-28)
-----------------

* moved code to codespeak.net subversion.

* reorganized package structure so that source code is under 'src' directory.
  Non-package files remain in distribution root.

* redid doc/.py files as doc/.txt, using more modern doctest. Before they
  were .py files with big docstrings.

* added test.py testrunner, and tests/test_icalendar.py that picks up all
  doctests in source code and doc directory, and runs them, when typing::

    python2.3 test.py

* renamed iCalendar to lower case package name, lowercased, de-pluralized and
  shorted module names, which are mostly implementation detail.

* changed tests so they generate .ics files in a temp directory, not in the structure itself.
