Versions and branches
=====================



Semantic versioning
-------------------

We use `Semantic Versioning <https://semver.org>`_.

-   Breaking changes increase the **major** version number.
-   New features increase the **minor** version number.
-   Minor changes and bug fixes increase the **patch** version number.
-   Stable release numbers consist of three numbers separated by two dots, such as 7.0.0 or 6.3.12.
-   Unstable releases are denoted by ``a``, ``b``, or ``rc``, such as ``7.0.0a1``.

.. _branch-policy:

Branches
--------

This section describes the branches used in icalendar development.

``main``
    The `main <https://github.com/collective/icalendar/tree/main/>`_ branch receives the latest updates and features.
    Active development takes place on this branch.
    It is compatible with Python versions 3.10 - 3.14, and PyPy3.10.

``7.x``
    icalendar version 7 is on the branch `7.x <https://github.com/collective/icalendar/tree/7.x/>`_.
    It is compatible with Python versions 3.10 - 3.14, and PyPy3.10.

``6.x``
    icalendar version 6 is on the branch `6.x <https://github.com/collective/icalendar/tree/6.x/>`_.
    It is compatible with Python versions 3.8 - 3.13, and PyPy3.9.
    Security updates and bug fixes can be backported and added to ``6.x`` on request.

``5.x``
    icalendar version 5 is on the branch `5.x <https://github.com/collective/icalendar/tree/5.x/>`_.
    It is compatible with Python versions 3.7 - 3.11, and PyPy3.9.
    Security updates and bug fixes can be backported and added to ``5.x`` on request.

``4.x``
    icalendar version 4 is on the branch `4.x <https://github.com/collective/icalendar/tree/4.x/>`_.
    It is compatible with Python versions 2.7, 3.4 - 3.10, and PyPy2.7 and PyPy3.9.
    Security updates and bug fixes can be backported and added to ``4.x`` on request.

.. seealso::

    `icalendar security policy <https://github.com/collective/icalendar/security/policy>`_.
