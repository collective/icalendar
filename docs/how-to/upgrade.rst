=============
Upgrade guide
=============

This chapter describes how to upgrade icalendar to the latest version from previous versions.
Its purpose is to help developers adapt their existing code.

This guide includes only breaking changes and deprecation notices.
For a comprehensive list of new features and bug fixes, see the :doc:`../reference/changelog`.

.. _upgrade-8.0.0:

8.0.0
=====

This section describes the major changes to icalendar in version 8.0.0.

.. _upgrade-8.0.0-breaking:

Breaking changes
----------------

This section describes the breaking changes in icalendar 8.0.0, and how to adapt your code to these changes.

.. _upgrade-8.0.0-parsing-errors:

Parsing errors are recorded by default
''''''''''''''''''''''''''''''''''''''

All components now ignore parsing exceptions by default, resolving :issue:`399`.
Malformed content lines and property values are skipped or represented as broken properties, and the exception is recorded in the component's ``errors`` attribute.
See :doc:`parse-errors` for how to inspect errors and broken properties, and :attr:`Component.ignore_exceptions <icalendar.cal.component.Component.ignore_exceptions>` for the parsing setting.

**Restore the old strict behavior**

If your code relies on :meth:`Component.from_ical <icalendar.cal.component.Component.from_ical>` raising ``ValueError`` for malformed content, set ``Component.ignore_exceptions = False`` before parsing.
The following example parses an existing calendar fixture containing a malformed bare ``X`` line.

.. code-block:: pycon

    >>> from icalendar import Component, Calendar
    >>> previous_ignore_exceptions = Component.ignore_exceptions
    >>> Component.ignore_exceptions = False
    >>> Calendar.example("issue_104_broken_calendar")
    Traceback (most recent call last):
        ...
    ValueError: Content line could not be parsed into parts: 'X': Invalid content line
    >>> # Restore the process-wide setting after the example.
    >>> Component.ignore_exceptions = previous_ignore_exceptions

**Enable tolerant behavior on older versions**

Set ``Component.ignore_exceptions = True`` before parsing to record errors instead of raising them.
Inspect ``errors`` on the component that contains the malformed content.

.. code-block:: pycon

    >>> from icalendar import Component
    >>> from icalendar import Calendar
    >>> previous_ignore_exceptions = Component.ignore_exceptions
    >>> Component.ignore_exceptions = True
    >>> calendar = Calendar.example("issue_104_broken_calendar")
    >>> calendar.errors
    [(None, "Content line could not be parsed into parts: 'X': Invalid content line")]
    >>> b"\r\nX\r\n" in calendar.to_ical()
    False
    >>> # Restore the process-wide setting after the example.
    >>> Component.ignore_exceptions = previous_ignore_exceptions

**Scope and exceptions**

This is a process-wide class setting.
Creating a subclass of ``Calendar`` doesn't change the component classes created by the component factory.
As in older versions, ``Event.ignore_exceptions = True`` remains an explicit override, so events stay tolerant when only ``Component.ignore_exceptions`` is set to ``False``.

Strict components raise for malformed content lines and most malformed property values.
The existing parser exception for malformed ``X-*`` property values remains tolerant even when ``ignore_exceptions`` is ``False``; those errors are recorded and the properties are represented as broken values.

``Component.from_ical`` no longer reads files from a ``str`` path
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

:meth:`Component.from_ical <icalendar.cal.component.Component.from_ical>` no longer reads a file when it is given a ``str`` that matches a path on the file system.
``str`` and ``bytes`` values are now always parsed as iCalendar data.
This prevents untrusted input from causing unintended local file reads.

If your code passes a file path as a ``str``:

.. code-block:: python

    from icalendar import Calendar

    calendar = Calendar.from_ical("/path/to/calendar.ics")

…then pass a :class:`pathlib.Path` instead.

.. code-block:: python

    from pathlib import Path

    from icalendar import Calendar

    calendar = Calendar.from_ical(Path("/path/to/calendar.ics"))


.. _upgrade-7.0.0:

7.0.0
=====

This section describes the major changes to icalendar in version 7.0.0.

.. _upgrade-7.0.0-breaking:

Developers may be concerned about upgrading to a **new major** release.
Upgrading from 6.x to 7.x should have **no complications for most developers**, because:

- the core API stays compatible with 4.x
- the breaking changes likely affect you only if you are an icalendar expert, not a normal user

We still recommend checking out the new features and giving feedback in the repository.

Breaking changes
----------------

This section describes the breaking changes in icalendar 7.0.0, and how to adapt your code to these changes.

Python 3.8 and 3.9 support
''''''''''''''''''''''''''

Python 3.8 and 3.9 have reached end of life.

Support for Python 3.8 and 3.9 is removed in icalendar 7.0.0.

.. seealso::

    -   `Status of Python versions <https://devguide.python.org/versions/#versions>`_
    -   `GitHub Actions Python support policy <https://github.com/actions/python-versions#support-policy>`_

``Component.decoded`` return type changed
'''''''''''''''''''''''''''''''''''''''''

The method :meth:`Component.decoded <icalendar.cal.component.Component.decoded>` now returns a string instead of bytes for text properties.


Property creation error change
''''''''''''''''''''''''''''''

icalendar now correctly throws a ``TypeError`` for wrong types during property creation, instead of a ``ValueError``.

If your code expects a ``ValueError`` when creating a property, then you should change your code to use ``TypeError``.


Moved ``types_factory``
'''''''''''''''''''''''

``types_factory`` was moved into :attr:`Component.types_factory <icalendar.cal.component.Component.types_factory>`.

Adjust your imports from the old location of ``types_factory``:

.. code-block:: python

    from icalendar import cal

…to the new location.

.. code-block:: python

    from icalendar.cal.component import Component


Moved ``components_factory``
''''''''''''''''''''''''''''

``components_factory`` was moved into :attr:`Component.get_component_class <icalendar.cal.component.Component.get_component_class>`.

Adjust your imports from the old location of ``components_factory``:

.. code-block:: python

    from icalendar import cal

…to the new location.

.. code-block:: python

    from icalendar.cal.component import Component


Moved ``IncompleteComponent``
'''''''''''''''''''''''''''''

The error ``icalendar.cal.IncompleteComponent`` was moved to :exc:`icalendar.error.IncompleteComponent`.

Adjust your imports from the old location of ``IncompleteComponent``:

.. code-block:: python

    from icalendar.cal import IncompleteComponent

…to the new location.

.. code-block:: python

    from icalendar.error import IncompleteComponent


Removed ``icalendar.UIDGenerator``
''''''''''''''''''''''''''''''''''

``icalendar.UIDGenerator`` was removed.
Use the Python standard library's :mod:`uuid` module instead.


.. _upgrade-6.0.0:

6.0.0
=====

This section describes the major changes to icalendar in version 6.0.0.


.. _upgrade-6.0.0-deprecation:

Deprecations
------------

The following deprecation notice describes which features may be removed in a future major release of icalendar.


``pytz`` support
''''''''''''''''

:mod:`zoneinfo` is the recommended replacement for `pytz <https://pypi.org/project/pytz/>`_.
``zoneinfo`` was added in Python 3.9, and is not available in Python 3.8.

In icalendar 6.0.0a, full support for ``zoneinfo`` was added.
``pytz`` may still be used, but developers are encouraged to follow the advice of the maintainers of ``pytz`` and move to ``zoneinfo``.
