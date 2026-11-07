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


..  _vbinary-obj-removed:

``vBinary.obj`` removed
'''''''''''''''''''''''

``vBinary.obj`` corrupted data.
Use :meth:`vBinary.bytes <icalendar.prop.binary.vBinary.bytes>` instead.

The example below shows how to correctly access binary data:

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> cal = Calendar.example("rfc_7986_image.ics")
    >>> v_binary = cal.events[1]["IMAGE"]
    >>> v_binary.bytes[:4]  # correct access for PNG image data
    b'\x89PNG'

For backward compatibility, if corrupt data is acceptable and you need to get the bytes as a Unicode string, decode them with ``errors="replace"`` as shown in the following code:

.. code-block:: pycon

    >>> string = v_binary.bytes.decode("utf-8", errors="replace")  # corrupts data

..  _removed-from-icalendar-parser-string:

Functions removed from :mod:`icalendar.parser.string`
'''''''''''''''''''''''''''''''''''''''''''''''''''''

These functions have been removed from :mod:`icalendar.parser.string`:

* ``escape_char``
* ``escape_string``
* ``foldline``,
* ``unescape_char``
* ``unescape_string``

..  _from-ical-not-utf-8:

``Component.from_ical`` raises an error for data that is not UTF-8
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

:meth:`Component.from_ical <icalendar.cal.component.Component.from_ical>` used to replace bytes that are not valid UTF-8 with ``�``, which silently corrupted the text.
It now raises an :class:`~icalendar.error.ICalDecodeError` instead.

If you know the encoding of the data, decode it yourself and pass the string:

.. code-block:: python

    calendar = Calendar.from_ical(data.decode("cp1252"))

If you want the previous behavior, decode the data with ``errors="replace"``:

.. code-block:: python

    calendar = Calendar.from_ical(data.decode("utf-8", errors="replace"))

See :doc:`parse-errors` for more information.


.. _upgrade-8.0.0-prek:

Migrate from pre-commit to prek
-------------------------------

icalendar now uses `prek <https://prek.j178.dev/>`_ instead of :program:`pre-commit` to manage its Git hooks.

If you have an existing development environment with :program:`pre-commit` hooks installed, first back up any custom hooks.
Then replace all hooks by running the following command once.

.. code-block:: shell

    uv run prek install -f

The ``-f`` option overwrites existing hook scripts in :file:`.git/hooks`.


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
