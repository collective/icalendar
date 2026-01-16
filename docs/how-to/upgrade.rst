=============
Upgrade guide
=============

This chapter describes how to upgrade icalendar to the latest version from previous versions.
Its purpose is to help developers adapt their existing code.

This guide includes only breaking changes and deprecation notices.
For a comprehensive list of new features and bug fixes, see the :doc:`../reference/changelog`.


.. _upgrade-7.0.0:

7.0.0
=====

This section describes the major changes to icalendar in version 7.0.0.

.. _upgrade-7.0.0-breaking:

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
