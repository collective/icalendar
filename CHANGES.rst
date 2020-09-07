Changelog
=========

4.0.7 (2020-09-07)
------------------

Bug fixes:

- fixed rrule handling, re-enabled test_create_america_new_york()


4.0.6 (2020-05-06)
------------------

Bug fixes:

- Use ``vText`` as default type, when convert recurrence definition to ical string. [kam193] 


4.0.5 (2020-03-21)
------------------

Bug fixes:

- Fixed a docs issue related to building on Read the Docs [davidfischer]


4.0.4 (2019-11-25)
------------------

Bug fixes:

- Reduce Hypothesis iterations to speed up testing, allowing PRs to pass
  [UniversalSuperBox]


4.0.3 (2018-10-10)
------------------

Bug fixes:

- Categories are comma separated not 1 per line #265. [cleder]
- mark test with mixed timezoneaware and naive datetimes as an expected failure. [cleder]


4.0.2 (2018-06-20)
------------------

Bug fixes:

- Update all pypi.python.org URLs to pypi.org
  [jon.dufresne]


4.0.1 (2018-02-11)
------------------

- Added rudimentary command line interface.
  [jfjlaros]

- Readme, setup and travis updates.
  [jdufresne, PabloCastellano]


4.0.0 (2017-11-08)
------------------

Breaking changes:

- Drop support for Python 2.6 and 3.3.


3.12 (2017-11-07)
-----------------

New features:

- Accept Windows timezone identifiers as valid. #242 [geier]

Bug fixes:

- Fix ResourceWarnings in setup.py when Python warnings are enabled. #244 [jdufresne]

- Fix invalid escape sequences in string and bytes literals. #245 [jdufresne]

- Include license file in the generated wheel package. #243 [jdufresne]

- Fix non-ASCII TZID and TZNAME parameter handling. #238 [clivest]

- Docs: update install instructions. #240 [Ekran]


3.11.7 (2017-08-27)
-------------------

New features:

- added vUTCOffset.ignore_exceptions to allow surpressing of failed TZOFFSET
  parsing (for now this ignores the check for offsets > 24h) [geier]


3.11.6 (2017-08-04)
-------------------

Bug fixes:

- Fix VTIMEZONEs including RDATEs #234.  [geier]


3.11.5 (2017-07-03)
-------------------

Bug fixes:

- added an assertion that VTIMEZONE sub-components' DTSTART must be of type
  DATETIME [geier]

- Fix handling of VTIMEZONEs with subcomponents with the same DTSTARTs and
  OFFSETs but which are of different types  [geier]


3.11.4 (2017-05-10)
-------------------

Bug fixes:

- Don't break on parameter values which contain equal signs, e.g. base64 encoded
  binary data [geier]

- Fix handling of VTIMEZONEs with subcomponents with the same DTSTARTs.
  [geier]


3.11.3 (2017-02-15)
-------------------

Bug fixes:

- Removed ``setuptools`` as a dependency as it was only required by setup.py
  and not by the package.

- Don't split content lines on the unicode ``LINE SEPARATOR`` character
  ``\u2028`` but only on ``CRLF`` or ``LF``.

3.11.2 (2017-01-12)
-------------------

Bug fixes:

- Run tests with python 3.5 and 3.6.
  [geier]

- Allow tests failing with pypy3 on travis.ci.
  [geier]


3.11.1 (2016-12-19)
-------------------

Bug fixes:

- Encode error message before adding it to the stack of collected error messages.


3.11 (2016-11-18)
-----------------

Fixes:

- Successfully test with pypy and pypy3.  [gforcada]

- Minor documentation update.  [tpltnt]


3.10 (2016-05-26)
-----------------

New:

- Updated components description to better comply with RFC 5545.
  Refs #183.
  [stlaz]

- Added PERIOD value type to date types.
  Also fixes incompatibilities described in #184.
  Refs #189.
  [stlaz]

Fixes:

- Fix testsuite for use with ``dateutil>=2.5``.
  Refs #195.
  [untitaker]

- Reintroduce cal.Component.is_broken that was removed with 3.9.2.
  Refs #185.
  [geier]


3.9.2 (2016-02-05)
------------------

New:

- Defined ``test_suite`` in setup.py.
  Now tests can be run via ``python setup.py test``.
  [geier]

Fixes:

- Fixed cal.Component.from_ical() representing an unknown component as one of the known.
  [stlaz]

- Fixed possible IndexError exception during parsing of an ical string.
  [stlaz]

- When doing a boolean test on ``icalendar.cal.Component``, always return ``True``.
  Before it was returning ``False`` due to CaselessDict, if it didn't contain any items.
  [stlaz]

- Fixed date-time being recognized as date or time during parsing.
  Added better error handling to parsing from ical strings.
  [stlaz]

- Added __version__ attribute to init.py.
  [TomTry]

- Documentation fixes.
  [TomTry]

- Pep 8, UTF 8 headers, dict/list calls to literals.
  [thet]


3.9.1 (2015-09-08)
------------------

- Fix ``vPeriod.__repr__``.
  [spacekpe]

- Improve foldline() performance. This improves the foldline performance,
  especially for large strings like base64-encoded inline attachements. In some
  cases (1MB string) from 7 Minutes to less than 20ms for ASCII data and 500ms
  for non-ASCII data. Ref: #163.
  [emfree]


3.9.0 (2015-03-24)
------------------

- Creating timezone objects from VTIMEZONE components.
  [geier]

- Make ``python-dateutil`` a dependency.
  [geier]

- Made RRULE tolerant of trailing semicolons.
  [sleeper]

- Documentation fixes.
  [t-8ch, thet]

3.8.4 (2014-11-01)
------------------

- Add missing BYWEEKNO to recurrence rules.
  [russkel]


3.8.3 (2014-08-26)
------------------

- PERCENT property in VTODO renamed to PERCENT-COMPLETE, according to RFC5545.
  [thomascube]


3.8.2 (2014-07-22)
------------------

- Exclude editor backup files from egg distributions. Fixes #144.
  [thet]


3.8.1 (2014-07-17)
------------------

- The representation of CaselessDicts in 3.8 changed the name attribute of
  Components and therefore broke the external API. This has been fixed.
  [untitaker]


3.8 (2014-07-17)
----------------

- Allow dots in property names (Needed for vCard compatibility). Refs #143.
  [untitaker]

- Change class representation for CaselessDict objects to always include the
  class name or the class' name attribute, if available. Also show
  subcomponents for Component objects.
  [thet]

- Don't use data_encode for CaselessDict class representation but use dict's
  __repr__ method.
  [t-8ch]

- Handle parameters with multiple values, which is needed for vCard 3.0.
  Refs #142.
  [t-8ch]


3.7 (2014-06-02)
----------------

- For components with ``ignore_exceptions`` set to ``True``, mark unparseable
  lines as broken instead rising a ``ValueError``. ``VEVENT`` components have
  ``ignore_exceptions`` set to ``True`` by default. Ref #131. Fixes #104.
  [jkiang13]

- Make ``python-dateutil`` a soft-dependency.
  [boltnev]

- Add optional ``sorted`` parameter to ``Component.to_ical``. Setting it to
  false allows the user to preserve the original property and parameter order.
  Ref #136. Fixes #133.
  [untitaker]

- Fix tests for latest ``pytz``. Don't set ``tzinfo`` directly on datetime
  objects, but use pytz's ``localize`` function. Ref #138.
  [untitaker, thet]

- Remove incorrect use of __all__. We don't encourage using ``from package
  import *`` imports. Fixes #129.
  [eric-wieser]


3.6.2 (2014-04-05)
------------------

- Pep8 and cleanup.
  [lasudry]

3.6.1 (2014-01-13)
------------------

- Open text files referenced by setup.py as utf-8, no matter what the locale
  settings are set to. Fixes #122.
  [sochotnicky]

- Add tox.ini to source tarball, which simplifies testing for in distributions.
  [sochotnicky]


3.6 (2014-01-06)
----------------

- Python3 (3.3+) + Python 2 (2.6+) support [geier]

- Made sure to_ical() always returns bytes [geier]

- Support adding lists to a component property, which value already was a list
  and remove the Component.set method, which was only used by the add method.
  [thet]

- Remove ability to add property parameters via a value's params attribute when
  adding via cal.add (that was only possible for custom value objects and makes
  up a strange API), but support a parameter attribute on cal.add's method
  signature to pass a dictionary with property parameter key/value pairs.
  Fixes #116.
  [thet]

- Backport some of Regebro's changes from his regebro-refactor branch.
  [thet]

- Raise explicit error on another malformed content line case.
  [hajdbo]

- Correctly parse datetime component property values with timezone information
  when parsed from ical strings.
  [untitaker]


3.5 (2013-07-03)
----------------

- Let to_unicode be more graceful for non-unicode strings, as like CMFPlone's
  safe_unicode does it.
  [thet]


3.4 (2013-04-24)
----------------

- Switch to unicode internally. This should fix all en/decoding errors.
  [thet]

- Support for non-ascii parameter values. Fixes #88.
  [warvariuc]

- Added functions to transform chars in string with '\\' + any of r'\,;:' chars
  into '%{:02X}' form to avoid splitting on chars escaped with '\\'.
  [warvariuc]

- Allow seconds in vUTCOffset properties. Fixes #55.
  [thet]

- Let ``Component.decode`` better handle vRecur and vDDDLists properties.
  Fixes #70.
  [thet]

- Don't let ``Component.add`` re-encode already encoded values. This simplifies
  the API, since there is no need explicitly pass ``encode=False``. Fixes #82.
  [thet]

- Rename tzinfo_from_dt to tzid_from_dt, which is what it does.
  [thet]

- More support for dateutil parsed tzinfo objects. Fixes #89.
  [leo-naeka]

- Remove python-dateutil version fix at all. Current python-dateutil has Py3
  and Py2 compatibility.
  [thet]

- Declare the required python-dateutil dependency in setup.py. Fixes #90.
  [kleink]

- Raise test coverage.
  [thet]

- Remove interfaces module, as it is unused.
  [thet]

- Remove ``test_doctests.py``, test suite already created properly in
  ``test_icalendar.py``.
  [rnix]

- Transformed doctests into unittests, Test fixes and cleanup.
  [warvariuc]


3.3 (2013-02-08)
----------------

- Drop support for Python < 2.6.
  [thet]

- Allow vGeo to be instantiated with list and not only tuples of geo
  coordinates. Fixes #83.
  [thet]

- Don't force to pass a list to vDDDLists and allow setting individual RDATE
  and EXDATE values without having to wrap them in a list.
  [thet]

- Fix encoding function to allow setting RDATE and EXDATE values and not to
  have bypass encoding with an icalendar property.
  [thet]

- Allow setting of timezone for vDDDLists and support timezone properties for
  RDATE and EXDATE component properties.
  [thet]

- Move setting of TZID properties to vDDDTypes, where it belongs to.
  [thet]

- Use @staticmethod decorator instead of wrapper function.
  [warvariuc, thet]

- Extend quoting of parameter values to all of those characters: ",;: â'".
  This fixes an outlook incompatibility with some characters. Fixes: #79,
  Fixes: #81.
  [warvariuc]

- Define VTIMETZONE subcomponents STANDARD and DAYLIGHT for RFC5545 compliance.
  [thet]


3.2 (2012-11-27)
----------------

- Documentation file layout restructuring.
  [thet]

- Fix time support. vTime events can be instantiated with a datetime.time
  object, and do not inherit from datetime.time itself.
  [rdunklau]

- Correctly handle tzinfo objects parsed with dateutil. Fixes #77.
  [warvariuc, thet]

- Text values are escaped correclty. Fixes #74.
  [warvariuc]

- Returned old folding algorithm, as the current implementation fails in some
  cases. Fixes #72, Fixes #73.
  [warvariuc]

- Supports to_ical() on date/time properties for dates prior to 1900.
  [cdevienne]


3.1 (2012-09-05)
----------------

- Make sure parameters to certain properties propagate to the ical output.
  [kanarip]

- Re-include doctests.
  [rnix]

- Ensure correct datatype at instance creation time in ``prop.vCalAddress``
  and ``prop.vText``.
  [rnix]

- Apply TZID parameter to datetimes parsed from RECURRENCE-ID
  [dbstovall]

- Localize datetimes for timezones to avoid DST transition errors.
  [dbstovall]

- Allow UTC-OFFSET property value data types in seconds, which follows RFC5545
  specification.
  [nikolaeff]

- Remove utctz and normalized_timezone methods to simplify the codebase. The
  methods were too tiny to be useful and just used at one place.
  [thet]

- When using Component.add() to add icalendar properties, force a value
  conversion to UTC for CREATED, DTSTART and LAST-MODIFIED. The RFC expects UTC
  for those properties.
  [thet]

- Removed last occurrences of old API (from_string).
  [Rembane]

- Add 'recursive' argument to property_items() to switch recursive listing.
  For example when parsing a text/calendar text including multiple components
  (e.g. a VCALENDAR with 5 VEVENTs), the previous situation required us to look
  over all properties in VEVENTs even if we just want the properties under the
  VCALENDAR component (VERSION, PRODID, CALSCALE, METHOD).
  [dmikurube]

- All unit tests fixed.
  [mikaelfrykholm]


3.0.1b2 (2012-03-01)
--------------------

- For all TZID parameters in DATE-TIME properties, use timezone identifiers
  (e.g. Europe/Vienna) instead of timezone names (e.g. CET), as required by
  RFC5545. Timezone names are used together with timezone identifiers in the
  Timezone components.
  [thet]

- Timezone parsing, issues and test fixes.
  [mikaelfrykholm, garbas, tgecho]

- Since we use pytz for timezones, also use UTC tzinfo object from the pytz
  library instead of own implementation.
  [thet]


3.0.1b1 (2012-02-24)
--------------------

- Update Release information.
  [thet]


3.0
---

- Add API for proper Timezone support. Allow creating ical DATE-TIME strings
  with timezone information from Python datetimes with pytz based timezone
  information and vice versa.
  [thet]

- Unify API to only use to_ical and from_ical and remove string casting as a
  requirement for Python 3 compatibility:
  New: to_ical.
  Old: ical, string, as_string and string casting via __str__ and str.
  New: from_ical.
  Old: from_string.
  [thet]


2.2 (2011-08-24)
----------------

- migration to https://github.com/collective/icalendar using svn2git preserving
  tags, branches and authors.
  [garbas]

- using tox for testing on python 2.4, 2.5, 2.6, 2.6.
  [garbas]

- fixed tests so they pass also under python 2.7.
  [garbas]

- running tests on https://jenkins.plone.org/job/icalendar (only 2.6 for now)
  with some other metrics (pylint, clonedigger, coverage).
  [garbas]

- review and merge changes from https://github.com/cozi/icalendar fork.
  [garbas]

- created sphinx documentation and started documenting development and goals.
  [garbas]

- hook out github repository to http://readthedocs.org service so sphinx
  documentation is generated on each commit (for master). Documentation can be
  visible on: http://readthedocs.org/docs/icalendar/en/latest/
  [garbas]


2.1 (2009-12-14)
----------------

- Fix deprecation warnings about ``object.__init__`` taking no parameters.

- Set the VALUE parameter correctly for date values.

- Long binary data would be base64 encoded with newlines, which made the
  iCalendar files incorrect. (This still needs testing).

- Correctly handle content lines which include newlines.


2.0.1 (2008-07-11)
------------------

- Made the tests run under Python 2.5+

- Renamed the UTC class to Utc, so it would not clash with the UTC object,
  since that rendered the UTC object unpicklable.


2.0 (2008-07-11)
----------------

- EXDATE and RDATE now returns a vDDDLists object, which contains a list
  of vDDDTypes objects. This is do that EXDATE and RDATE can contain
  lists of dates, as per RFC.

  ***Note!***: This change is incompatible with earlier behavior, so if you
  handle EXDATE and RDATE you will need to update your code.

- When createing a vDuration of -5 hours (which in itself is nonsensical),
  the ical output of that was -P1DT19H, which is correct, but ugly. Now
  it's '-PT5H', which is prettier.


1.2 (2006-11-25)
----------------

- Fixed a string index out of range error in the new folding code.


1.1 (2006-11-23)
----------------

- Fixed a bug in caselessdicts popitem. (thanks to Michael Smith
  <msmith@fluendo.com>)

- The RFC 2445 was a bit unclear on how to handle line folding when it
  happened to be in the middle of a UTF-8 character. This has been clarified
  in the following discussion:
  http://lists.osafoundation.org/pipermail/ietf-calsify/2006-August/001126.html
  And this is now implemented in iCalendar. It will not fold in the middle of
  a UTF-8 character, but may fold in the middle of a UTF-8 composing character
  sequence.


1.0 (2006-08-03)
----------------

- make get_inline and set_inline support non ascii codes.

- Added support for creating a python egg distribution.


0.11 (2005-11-08)
-----------------

- Changed component .from_string to use types_factory instead of hardcoding
  entries to 'inline'

- Changed UTC tzinfo to a singleton so the same one is used everywhere

- Made the parser more strict by using regular expressions for key name,
  param name and quoted/unquoted safe char as per the RFC

- Added some tests from the schooltool icalendar parser for better coverage

- Be more forgiving on the regex for folding lines

- Allow for multiple top-level components on .from_string

- Fix vWeekdays, wasn't accepting relative param (eg: -3SA vs -SA)

- vDDDTypes didn't accept negative period (eg: -P30M)

- 'N' is also acceptable as newline on content lines, per RFC


0.10 (2005-04-28)
-----------------

- moved code to codespeak.net subversion.

- reorganized package structure so that source code is under 'src' directory.
  Non-package files remain in distribution root.

- redid doc/.py files as doc/.txt, using more modern doctest. Before they
  were .py files with big docstrings.

- added test.py testrunner, and tests/test_icalendar.py that picks up all
  doctests in source code and doc directory, and runs them, when typing::

    python2.3 test.py

- renamed iCalendar to lower case package name, lowercased, de-pluralized and
  shorted module names, which are mostly implementation detail.

- changed tests so they generate .ics files in a temp directory, not in the
  structure itself.
