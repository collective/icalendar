============
Contributing
============

This guide describes how to contribute to icalendar.

Examples of how to contribute
-----------------------------

-   Report issues in the `issue tracker <https://github.com/collective/icalendar/issues>`_.
-   Submit pull requests from your fork of the icalendar repository.
-   Extend the documentation.
-   Sponsor development of icalendar through `Open Collective <https://opencollective.com/python-icalendar>`_.


Pull request requirements
-------------------------

Before submitting your pull request, ensure you have met the following requirements.

#.  Add a changelog entry to :file:`CHANGES.rst`.
    This is required and enforced by GitHub checks.
    See :ref:`change-log` for details.
#.  Add a test which proves your fix and passes.
#.  Run all tests to ensure your changes don't break any existing functionality.
#.  Add or edit documentation, both as docstrings to be rendered in the API documentation and narrative documentation, as necessary.
#.  Add yourself to :file:`docs/credits.rst`, if you haven't already done so.


.. _change-log:

Change log entry format
```````````````````````

Add your entry under the appropriate section in :file:`CHANGES.rst`.

Minor changes
    For small improvements, refactoring, and documentation updates.

Breaking changes
    For changes that break the existing API.

New features
    For new functionality.

Bug fixes
    For bug fixes and error corrections.

Example:

.. code-block:: rst

    Minor changes:

    - Fix issue with timezone parsing in special cases. See `Issue XXX <link>`_.


Set up for development
----------------------

If you would like to set up icalendar to contribute changes, see :doc:`development`.



.. toctree::
    :hidden:

    development
    credits
    maintenance
