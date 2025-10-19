==========
Change log
==========

We use `Semantic Versioning <https://semver.org>`_.

- Breaking changes increase the **major** version number.
- New features increase the **minor** version number.
- Minor changes and bug fixes increase the **patch** version number.

7.0.0 (unreleased)
------------------

Minor changes:

- Split up ``cal.py`` into different files as sub-package.
- Format more source code with ruff.
- Exclude type checking block from test coverage.
- Add private ``icalendar.compatibility`` module to merge functionality for older Python versions into one place.
- Add type annotation to ``from_ical()``.
- Fix enum documentation.
- ``DTSTAMP``, ``LAST_MODIFIED``, and ``CREATED`` can now be set to ``None`` to delete the value.
- Enhanced ``Calendar.new()`` to support organization and language parameters for automatic ``PRODID`` generation.
- Added ``duration`` setter to ``Event`` class for more intuitive event creation.
- Added ``validate()`` method to ``Calendar`` class for explicit validation of required properties and components.
- Add improved setters for ``start``, ``duration``, and ``end`` properties with explicit locking mechanisms to provide more flexible property manipulation while maintaining RFC 5545 compliance. The implementation includes comprehensive test coverage to ensure proper behavior and backward compatibility.
- Add ``new()`` method to ``vCalAddress`` class for consistent API usage. The method supports all RFC 5545 parameters including ``CN``, ``CUTYPE``, ``DELEGATED-FROM``, ``DELEGATED-TO``, ``DIR``, ``LANGUAGE``, ``PARTSTAT``, ``ROLE``, ``RSVP``, and ``SENT-BY``, with automatic ``mailto:`` prefix handling. See `Issue 870 <https://github.com/collective/icalendar/issues/870>`_.
- Refactor ``set_duration`` methods in ``Event`` and ``Todo`` classes to eliminate code duplication by extracting common logic into shared ``set_duration_with_locking()`` function in ``icalendar.attr``. See `Issue 886 <https://github.com/collective/icalendar/issues/886>`_.
- Consolidate duplicate logic patterns between ``Event`` and ``Todo`` classes by extracting shared functions in ``icalendar.attr`` for property setters, validation logic, and property access. This eliminates approximately 150 lines of duplicate code while maintaining 100% backward compatibility and RFC 5545 compliance. See `Issue 891 <https://github.com/collective/icalendar/issues/891>`_.
- Accept and ignore non-standard empty ``RDATE`` fields when parsing ICS files.
- Improve contributing documentation by adding a change log requirement, adding a pull request template, adding clear CI enforcement warnings, and updating ``README.rst``. See `Issue 890 <https://github.com/collective/icalendar/issues/890>`_.
- Make coverage submission optional for CI.
- Bump ``actions/setup-python`` version from 5 to 6 for CI.
- Add comment explaining tzdata dependency purpose to prevent confusion. See `Issue 900 <https://github.com/collective/icalendar/issues/900>`_.
- Fix duplicate blank issue template by adding config.yml to disable GitHub's default blank option. See `Issue 777 <https://github.com/collective/icalendar/issues/777>`_.
- Add PEP 561 py.typed marker to enable type checking support. The package now distributes inline type annotations for mypy and other type checkers. See `Issue 395 <https://github.com/collective/icalendar/issues/395>`_.
- Bump ``github/codeql-action`` from 3 to 4 in CI fuzzing workflow.

Breaking changes:

- Correctly throw a ``TypeError`` for wrong types during property creation where a ``ValueError`` was thrown before.
- Move ``types_factory`` into ``Component.types_factory``
- Move ``components_factory`` into ``Component.get_component_class``
- Move ``icalendar.cal.IncompleteComponent`` error into ``icalendar.error``.
- Remove ``icalendar.UIDGenerator``. Use Python's built-in `uuid library <https://docs.python.org/3/library/uuid.html>`_ instead.

New features:

- Add ``ics_value`` property in value types  which decodes to python native types.`Issue 876 <https://github.com/collective/icalendar/issues/876>`_.
- Add ``new()`` to ``icalendar.Calendar`` to set required attributes. See `Issue 569 <https://github.com/collective/icalendar/issues/569>`_.
- Add ``new()`` to ``Alarm``, ``Event``, ``Todo``, ``FreeBusy``, ``Component``, and ``Journal`` components. See `Issue 843 <https://github.com/collective/icalendar/issues/843>`_.
- Add ``value`` to ``Parameters`` to access the ``VALUE`` parameter.
- Add ``Availability`` and ``Available`` components from :rfc:`7953`. See `Issue 654 <https://github.com/collective/icalendar/issues/654>`_ and `Issue 864 <https://github.com/collective/icalendar/issues/864>`_.
- Add ``stamp``, ``last_modified``, ``created``, ``CREATED``, ``busy_type``, ``class``, ``comments``, ``contacts``, ``location``, ``organizer``, ``priority``, and ``url`` properties to components that use them.
- Add ``availabilities`` attribtue to ``Calendar``.
- Add ``status``, ``transparency``, and ``attendees`` properties. See `Issue 841 <https://github.com/collective/icalendar/issues/841>`_.
- Add ``uid`` property that is ``''`` by default and set automatically with ``new()``. See `Issue 315 <https://github.com/collective/icalendar/issues/315>`_.
- Make icalendar compatible with `RFC 7986 <https://www.rfc-editor.org/rfc/rfc7986.html>`_.
  - Add ``url``, ``source``, ``refresh_interval``, ``conferences``, and ``images`` properties to components.
- Add ``td`` property to ``vDDDTypes`` to make it compatible with ``timedelta`` value types.


Bug fixes:

- Fix read from stdin issue - See `Issue 821 <https://github.com/collective/icalendar/issues/821>`_.
- Fix invalid calendar: Parsing a date with TZID results in a datetime to not loose the timezone. See `Issue 187 <https://github.com/collective/icalendar/issues/187>`_.
- Fix timezone placement in ``add_missing_timezones()``: ``VTIMEZONE`` components now appear before ``VEVENT`` and other components that reference them. See `Issue 844 <https://github.com/collective/icalendar/issues/844>`_.
- Fixed ``Todo.duration`` and ``Event.duration`` to return ``DURATION`` property when set, even without ``DTSTART``. See `Issue 867 <https://github.com/collective/icalendar/issues/867>`_.

6.3.1 (2025-05-20)
------------------

Bug fixes:

- Remove forced quoting from parameters with space and single quote. See `Issue 836 <https://github.com/collective/icalendar/issues/836>`_.

6.3.0 (2025-05-15)
------------------

Minor changes:

- Deprecate ``icalendar.UIDGenerator``. See `Issue 816 <https://github.com/collective/icalendar/issues/816>`_.

New features:

- Add the ``uid`` property to ``Alarm``, ``Event``, ``Calendar``, ``Todo``, and ``Journal`` components. See `Issue 740 <https://github.com/collective/icalendar/issues/740>`_.

Bug fixes:

- Fix component equality where timezones differ for the datetimes but the times are actually equal. See `Issue 828 <https://github.com/collective/icalendar/issues/828>`_.
- Test that we can add an RRULE as a string. See `Issue 301 <https://github.com/collective/icalendar/issues/301>`_.
- Test that we support dateutil timezones as outlined in `Issue 336 <https://github.com/collective/icalendar/issues/336>`_.
- Build documentation on Read the Docs with the version identifier. See `Issue 826 <https://github.com/collective/icalendar/issues/826>`_.

6.2.0 (2025-05-07)
------------------

Minor changes:

- Use ``ruff`` to format the source code.
- Update project metadata to use License-Expression.
- Use ``tzp.localize(dt, None)`` to remove the timezone from a datetime.
- Remove the HTML documentation when building with ``tox`` to force rebuild.
- Switch to PyData Sphinx Theme for documentation. See `Issue 803 <https://github.com/collective/icalendar/issues/804>`_.

New features:

- Add getters ``rrules``, ``rdates``, and ``exdates`` for unified and simple access to these properties. See `Issue 662`_.
- Add attributes to the calendar for properties ``NAME``, ``DESCRIPTION``, and ``COLOR``. See `Issue 655 <https://github.com/collective/icalendar/issues/655>`_.
- Add a ``color`` attribute to ``Event``, ``Todo``, and ``Journal`` components. See `Issue 655`_.
- Add ``sequence`` attribute to ``Event``, ``Todo``, and ``Journal`` components. See `Issue 802 <https://github.com/collective/icalendar/issues/802>`_.
- Add ``categories`` attribute to ``Calendar``, ``Event``, ``Todo``, and ``Journal`` components. See `Issue 655 <https://github.com/collective/icalendar/issues/655>`_.
- Add compatibility to :rfc:`6868`. See `Issue 652 <https://github.com/collective/icalendar/issues/652>`_.
- Add ``freebusy`` property to the ``Calendar`` to get this type of subcomponents easier.
- Add parameters from :rfc:`5545` to properties ``ALTREP``, ``CN``, ``CUTYPE``, ``DELEGATED_FROM``, ``DELEGATED_TO``, ``DIR``, ``FBTYPE``, ``LANGUAGE``, ``MEMBER``, ``PARTSTAT``, ``RANGE``, ``RELATED``, ``ROLE``, ``RSVP``, ``SENT_BY``, ``TZID``, and ``RELTYPE``. See `Issue 798 <https://github.com/collective/icalendar/issues/798>`_.
- New properties from :rfc:`7986` can occur multiple times in ``VCALENDAR``. See `PR 808`_.

Bug fixes:

- Fix ``STANDARD`` and ``DAYLIGHT`` components that have a date as ``DTSTART``. See `Issue 218 <https://github.com/collective/icalendar/issues/218>`_
- Move import at the end of ``icalendar.parser`` into a function to mitigate import errors, see `Issue 781 <https://github.com/collective/icalendar/issues/781>`_.
- ``ALTREP``, ``DELEGATED-FROM``, ``DELEGATED-TO``, ``DIR``, ``MEMBER``, and ``SENT-BY`` require double quotes. These are now always added.
- Classify ``CATEGORIES`` as multiple in ``VEVENT``. See `PR 808 <https://github.com/collective/icalendar/pull/808>`_.

6.1.3 (2025-03-19)
------------------

Bug fixes:

- Fix to permit TZID forward references to ``VTIMEZONE``\ s
- Stabelize timezone id lookup, see `Issue 780 <https://github.com/collective/icalendar/issues/780>`_.

6.1.2 (2025-03-19)
------------------

Minor changes:

- Add funding link to Tidelift.
- Link to related package.
- Shorten first example in documentation.
- Add ``name`` and ``email`` properties to ``vCalAddress``.
- Add type hint for property ``params`` in ``icalendar.prop``.
- Set default value for ``params`` as ``params={}`` in mulitple constructors in ``icalendar.prop`` to improve usability.
- Improve object initialization performance in ``icalendar.prop``.
- Add type hint for ``params`` in multiple constructors in ``icalendar.prop``.

Bug fixes:

- Restrict timezones tested, see `Issue 763 <https://github.com/collective/icalendar/issues/763>`_

6.1.1 (2025-01-18)
------------------

Minor changes:

- Add a ``weekday`` attribute to :class:`icalendar.prop.vWeekday` components. See `Issue 749 <https://github.com/collective/icalendar/issues/749>`_.
- Document :class:`icalendar.prop.vRecur` property. See `Issue 758 <https://github.com/collective/icalendar/issues/758>`_.
- Print failure of doctest to aid debugging.
- Improve documentation of :class:`icalendar.prop.vGeo`
- Fix tests, improve code readability, fix typing. See `Issue 766 <https://github.com/collective/icalendar/issues/766>`_ and `Issue 765 <https://github.com/collective/icalendar/issues/765>`_.

Breaking changes:

- The ``relative`` attribute of ``vWeekday`` components has the correct sign now. See `Issue 749 <https://github.com/collective/icalendar/issues/749>`_.

New features:

- Add :ref:`Security Policy`
- Python types in documentation now link to their documentation pages using ``intersphinx``.

6.1.0 (2024-11-22)
------------------

Minor changes:

- Add ``end``, ``start``, ``duration``, ``DTSTART``, ``DUE``, and ``DURATION`` attributes to ``Todo`` components. See `Issue 662`_.
- Add ``DTSTART``, ``TZOFFSETTO`` and ``TZOFFSETFROM`` properties to ``TimezoneStandard`` and ``TimezoneDaylight``. See `Issue 662`_.
- Format test code with Ruff. See `Issue 672 <https://github.com/collective/icalendar/issues/672>`_.
- Document the Debian package. See `Issue 701 <https://github.com/collective/icalendar/issues/701>`_.
- Document ``vDatetime.from_ical``
- Allow passing a ``datetime.date`` to ``TZP.localize_utc`` and ``TZP.localize`` methods.
- Document component classes with description from :rfc:`5545`.
- Merge "File Structure" and "Overview" sections in the docs. See `Issue 626 <https://github.com/collective/icalendar/issues/626>`_.
- Update code blocks in ``usage.rst`` with the correct lexer.
- Tidy up the docstring for ``icalendar.prop.vPeriod``.
- Improve typing and fix typing issues


New features:

- Add ``VALARM`` properties for :rfc:`9074`. See `Issue 657 <https://github.com/collective/icalendar/issues/657>`_
- Test compatibility with Python 3.13
- Add ``Timezone.from_tzinfo()`` and ``Timezone.from_tzid()`` to create a ``Timezone`` component from a ``datetime.tzinfo`` timezone. See `Issue 722`_.
- Add ``icalendar.prop.tzid_from_tzinfo``.
- Add ``icalendar.alarms`` module to calculate alarm times. See `Issue 716 <https://github.com/collective/icalendar/issues/716>`_.
- Add ``Event.alarms`` and ``Todo.alarms`` to access alarm calculation.
- Add ``Component.DTSTAMP`` and ``Component.LAST_MODIFIED`` properties for datetime in UTC.
- Add ``Component.is_thunderbird()`` to check if the component uses custom properties by Thunderbird.
- Add ``X_MOZ_SNOOZE_TIME`` and ``X_MOZ_LASTACK`` properties to ``Event`` and ``Todo``.
- Add ``Alarm.ACKNOWLEDGED``, ``Alarm.TRIGGER``, ``Alarm.REPEAT``, and ``Alarm.DURATION`` properties
  as well as ``Alarm.triggers`` to calculate alarm triggers.
- Add ``__doc__`` string documentation for ``vDate``, ``vBoolean``, ``vCalAddress``, ``vDuration``, ``vFloat``, ``vGeo``, ``vInt``, ``vPeriod``, ``vTime``, ``vUTCOffset`` and ``vUri``. See `Issue 742 <https://github.com/collective/icalendar/issues/742>`_.
- Add ``DTSTART``, ``TZOFFSETTO``, and ``TZOFFSETFROM`` to ``TimezoneStandard`` and ``TimezoneDaylight``
- Use ``example`` methods of components without arguments.
- Add ``events``, ``timezones``, and ``todos`` property to ``Calendar`` for nicer access.
- To calculate which timezones are in use and add them to the ``Calendar`` when needed these methods are added: ``get_used_tzids``, ``get_missing_tzids``, and ``add_missing_timezones()``.
- Identify the TZID of more timezones from dateutil.
- Identify totally unknown timezones using a UTC offset lookup tree generated in ``icalendar.timezone.equivalent_timezone_ids`` and stored in ``icalendar.timezone.equivalent_timezone_ids``.
- Add ``icalendar.timezone.tzid`` to identify a timezone's TZID.

Bug fixes:

- Add ``icalendar.timezone`` to the documentation.

.. _`Issue 722`: https://github.com/collective/icalendar/issues/722

6.0.1 (2024-10-13)
------------------

New features:

- Added ``end``, ``start``, ``duration``, ``DTSTART``, ``DUE``, and ``DURATION`` attributes to ``Event`` components. See `Issue 662`_.
- Added ``end``, ``start``, ``duration``, and ``DTSTART`` attributes to ``Journal`` components. See `Issue 662`_.

Bug fixes:

- Fix a few ``__all__`` variables.
- Added missing ``docs`` folder to distribution packages. See `Issue 712 <https://github.com/collective/icalendar/issues/712>`_.

.. _`Issue 662`: https://github.com/collective/icalendar/issues/662

6.0.0 (2024-09-28)
------------------

Minor changes:

- Add ``__all__`` variable to each modules in ``icalendar`` package
- Improve test coverage.
- Adapt ``test_with_doctest.py`` to correctly run on Windows.
- Measure branch coverage when running tests.
- Export ``Component`` base class for typing

New features:

- Use ``pyproject.toml`` file instead of ``setup.py``

Bug fixes:

- Fix link to stable release of tox in documentation.
- Fix a bad ``bytes`` replace in ``unescape_char``.
- Handle ``ValueError`` in ``vBinary.from_ical``.
- Ignore the BOM character in incorrectly encoded ics files.

6.0.0a0 (2024-07-03)
--------------------

Minor changes:

- Test that all code works with both ``pytz`` and ``zoneinfo``.
- Add message to GitHub release, pointing to the changelog
- Make coverage report submission optional for pull requests
- Parallelize coverage
- Rename ``master`` branch to ``main``, see `Issue
  <https://github.com/collective/icalendar/issues/627>`_
- Update ``docs/usage.rst`` to use zoneinfo instead of pytz.
- Added missing public classes and functions to API documentation.
- Improved namespace management in the ``icalendar`` directory.
- Add Python version badge and badge for test coverage
- Remove 4.x badge
- Update list of ``tox`` environments
- Use Coveralls' GitHub Action
- Check distribution in CI

Breaking changes:

- Use ``zoneinfo`` for ``icalendar`` objects created from strings,
  see `Issue #609 <https://github.com/collective/icalendar/issues/609>`_.

  This is an tested extension of the functionality, not a restriction:
  If you create ``icalendar`` objects with ``pytz`` timezones in your code,
  ``icalendar`` will continue to work in the same way.
  Your code is not affected.

  ``zoneinfo`` will be used for those **objects that** ``icalendar``
  **creates itself**.
  This happens for example when parsing an ``.ics`` file, strings or bytes with
  ``from_ical()``.

  If you rely on ``icalendar`` providing timezones from ``pytz``, you can add
  one line to your code to get the behavior of versions below 6:

  .. code:: Python

      import icalendar
      icalendar.use_pytz()

- Replaced ``pkg_resources.get_distribution`` with ``importlib.metadata`` in
  ``docs/conf.py`` to allow building docs on Python 3.12.

- Remove ``is_broken`` property. Use ``errors`` instead to check if a
  component had suppressed parsing errors.
  See `Issue 424 <https://github.com/collective/icalendar/issues/424>`_.

- Remove untested and broken ``LocalTimezone`` and ``FixedOffset`` tzinfo
  sub-classes, see `Issue 67 <https://github.com/collective/icalendar/issues/67>`_

- Remove Python 3.7 as compatible. icalendar is compatible with Python
  versions 3.8 - 3.12, and PyPy3.

- Remove ``pytz`` as a dependency of ``icalendar``. If you require ``pytz``,
  add it to your dependency list or install it additionally with::

      pip install icalendar==6.* pytz

New features:

- Check code quality with `Ruff <https://docs.astral.sh/ruff/>`_, optional report
- Test compatibility with Python 3.12
- Add function ``icalendar.use_pytz()``.
- Allows selecting components with ``walk(select=func)`` where ``func`` takes a
  component and returns ``True`` or ``False``.
- Add compatibility to :rfc:`7529`, adding ``vMonth`` and ``vSkip``
- Add ``sphinx-autobuild`` for ``livehtml`` Makefile target.
- Add pull request preview on Read the Docs, building only on changes to documentation-related files.
- Add link to pull request preview builds in the pull request description only when there are changes to documentation-related files.
- Add documentation of live HTML preview of documentation and clean up of ``install.rst``.
- Add ``sphinx-copybutton`` to allow copying code blocks with a single click of a button.

Bug fixes:

- Change documentation to represent compatibility with Python 3.8 - 3.12, and PyPy3.
- Rename RFC 2445 to RFC 5545, see `Issue 278
  <https://github.com/collective/icalendar/issues/278>`_

5.0.13 (2024-06-20)
-------------------

Minor changes:

- Guide to delete the build folder before running tests
- Add funding information
- Make documentation build with Python 3.12
- Update windows to olson conversion for Greenland Standard Time
- Extend examples in Usage with alarm and recurrence
- Document how to serve the built documentation to view with the browser
- Improve test coverage

New features:

- Create GitHub releases for each tag.

Bug fixes:

- Parse calendars with X-COMMENT properties at the end the file by ignoring these properites


5.0.12 (2024-03-19)
-------------------

Minor changes:

- Analyse code coverage of test files
- Added corpus to fuzzing directory
- Added exclusion of fuzzing corpus in MANIFEST.in
- Augmented fuzzer to optionally convert multiple calendars from a source string
- Add script to convert OSS FUZZ test cases to Python/pytest test cases
- Added additional exception handling of defined errors to fuzzer, to allow fuzzer to explore deeper
- Added more instrumentation to fuzz-harness
- Rename "contributor" to "collaborator" in documentation
- Correct the outdated "icalendar view myfile.ics" command in documentation. #588
- Update GitHub Actions steps versions
- Keep GitHub Actions up to date with GitHub's Dependabot

Bug fixes:

- Fixed index error in cal.py when attempting to pop from an empty stack
- Fixed type error in prop.py when attempting to join strings into a byte-string
- Caught Wrong Date Format in ical_fuzzer to resolve fuzzing coverage blocker

5.0.11 (2023-11-03)
-------------------

Minor changes:

- The cli utility now displays start and end datetimes in the user's local timezone.
  Ref: #561
  [vimpostor]

New features:

- Added fuzzing harnesses, for integration to OSSFuzz.
- icalendar releases are deployed to Github releases
  Fixes: #563
  [jacadzaca]

Bug fixes:

- CATEGORIES field now accepts a string as argument
  Ref: #322
  [jacadzaca]
- Multivalue FREEBUSY property is now parsed properly
  Ref: #27
  [jacadzaca]
- Compare equality and inequality of calendars more completely
  Ref: #570
- Use non legacy timezone name.
  Ref: #567
- Add some compare functions.
  Ref: #568
- Change OSS Fuzz build script to point to harnesses in fuzzing directory
  Ref: #574

5.0.10 (2023-09-26)
-------------------

Bug fixes:

- Component._encode stops ignoring parameters argument on native values, now merges them
  Fixes: #557
  [zocker1999net]

5.0.9 (2023-09-24)
------------------

Bug fixes:

- PERIOD values now set the timezone of their start and end. #556

5.0.8 (2023-09-18)
------------------

Minor changes:

- Update build configuration to build readthedocs. #538
- No longer run the ``plone.app.event`` tests.
- Add documentation on how to parse ``.ics`` files. #152
- Move pip caching into Python setup action.
- Check that issue #165 can be closed.
- Updated about.rst for issue #527
- Avoid ``vText.__repr__`` BytesWarning.

Bug fixes:

- Calendar components are now properly compared
  Ref: #550
  Fixes: #526
  [jacadzaca]

5.0.7 (2023-05-29)
------------------

Bug fixes:

- to_ical() now accepts RRULE BYDAY values>=10 #518


5.0.6 (2023-05-26)
------------------

Minor changes:

- Adjusted duration regex

5.0.5 (2023-04-13)
------------------

Minor changes:

- Added support for BYWEEKDAY in vRecur ref: #268

Bug fixes:

- Fix problem with ORGANIZER in FREE/BUSY #348

5.0.4 (2022-12-29)
------------------

Minor changes:

- Improved documentation
  Ref: #503, #504

Bug fixes:

- vBoolean can now be used as an parameter
  Ref: #501
  Fixes: #500
  [jacadzaca]


5.0.3 (2022-11-23)
------------------

New features:

- vDDDTypes is hashable #487 #492 [niccokunzmann]

Bug fixes:

- vDDDTypes' equality also checks the dt attribute #497 #492 [niccokunzmann]

5.0.2 (2022-11-03)
------------------

Minor changes:

- Refactored cal.py, tools.py and completed remaining minimal refactoring in parser.py. Ref: #481 [pronoym99]
- Calendar.from_ical no longer throws long errors
  Ref: #473
  Fixes: #472
  [jacadzaca]
- Make datetime value shorter by removing the value parameter where possible.
  Fixes: #318
  [jacadzaca], [niccokunzmann]

New features:

- source code in documentation is tested using doctest #445 [niccokunzmann]

Bug fixes:

- broken properties are not added to the parent component
  Ref: #471
  Fixes: #464
  [jacadzaca]

5.0.1 (2022-10-22)
------------------

Minor changes:

- fixed setuptools deprecation warnings [mgorny]

Bug fixes:

- a well-known timezone timezone prefixed with a `/` is treated as if the slash wasn't present
  Ref: #467
  Fixes: #466
  [jacadzaca]

5.0.0 (2022-10-17)
------------------

Minor changes:

- removed deprecated test checks [tuergeist]
- Fix: cli does not support DURATION #354 [mamico]
- Add changelog and contributing to readthedocs documentation #428 [peleccom]
- fixed small typos #323 [rohnsha0]
- unittest to parametrized pytest refactoring [jacadzaca]

Breaking changes:

- Require Python 3.7 as minimum Python version.  [maurits] [niccokunzmann]
- icalendar now takes a ics file directly as an input
- icalendar's CLI utility program's output is different
- Drop Support for Python 3.6. Versions 3.7 - 3.11 are supported and tested.

New features:

- icalendar utility outputs a 'Duration' row
- icalendar can take multiple ics files as an input

Bug fixes:

- Changed tools.UIDGenerator instance methods to static methods
  Ref: #345
  [spralja]
- proper handling of datetime objects with `tzinfo` generated through zoneinfo.ZoneInfo.
  Ref: #334
  Fixes: #333
  [tobixen]
- Timestamps in UTC does not need tzid
  Ref: #338
  Fixes: #335
  [tobixen]
-  add ``__eq__`` to ``icalendar.prop.vDDDTypes`` #391 [jacadzaca]
- Refactor deprecated unittest aliases for Python 3.11 compatibility #330 [tirkarthi]

5.0.0a1 (2022-07-11)
--------------------

Breaking changes:

- Drop support for Python 3.4, 3.5 and PyPy2.  [maurits]

New features:

- Document development setup
  Ref: #358
  [niccokunzmann]

Bug fixes:

- Test with GitHub Actions.  [maurits]

4.1.0 (2022-07-11)
------------------

New features:

- No longer test on Python 3.4, 3.5 and PyPy2, because we cannot get it to work.
  Technically it should still work, it is just no longer tested.
  Do not expect much development on branch 4.x anymore.
  The main branch will be for the remaining Python versions that we support.
  [maurits]

Bug fixes:

- Test with GitHub Actions.  [maurits]

4.0.9 (2021-10-16)
------------------

Bug fixes:

- Fix vCategories for correct en/de coding.
  [thet]

- vDuration property value: Fix changing duration sign after multiple ``to_ical`` calls.
  Ref: #320
  Fixes: #319
  [barlik]


4.0.8 (2021-10-07)
------------------

Bug fixes:

- Support added for Python 3.9 and 3.10 (no code changes needed).

- Replace bare 'except:' with 'except Exception:' (#281)


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

- Fix ``VTIMEZONE``\ s including RDATEs #234.  [geier]


3.11.5 (2017-07-03)
-------------------

Bug fixes:

- added an assertion that ``VTIMEZONE`` sub-components' DTSTART must be of type
  DATETIME [geier]

- Fix handling of ``VTIMEZONE``\ s with subcomponents with the same DTSTARTs and
  OFFSETs but which are of different types  [geier]


3.11.4 (2017-05-10)
-------------------

Bug fixes:

- Don't break on parameter values which contain equal signs, e.g. base64 encoded
  binary data [geier]

- Fix handling of ``VTIMEZONE``\ s with subcomponents with the same DTSTARTs.
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

- Creating timezone objects from ``VTIMEZONE`` components.
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
  (e.g. a ``VCALENDAR`` with 5 ``VEVENT``s), the previous situation required us to look
  over all properties in ``VEVENT``s even if we just want the properties under the
  ``VCALENDAR`` component (VERSION, PRODID, CALSCALE, METHOD).
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

- hook out github repository to https://readthedocs.org service so sphinx
  documentation is generated on each commit (for main). Documentation can be
  visible on: https://icalendar.readthedocs.io/en/latest/
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
