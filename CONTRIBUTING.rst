You want to help and contribute? Perfect!
=========================================

These are some contribution examples
------------------------------------

- Reporting issues to the bugtracker.

- Submitting pull requests from a forked icalendar repo.

- Extending the documentation.

- Sponsor a Sprint (https://plone.org/events/sprints/whatis).


Pull Request Requirements
-------------------------

**Important:** Every pull request must include a changelog entry, or it will fail CI checks.

Before submitting your PR, ensure you have:

1. **Add a changelog entry to ``CHANGES.rst``** - This is required and enforced by CI
2. Add a test which proves your fix and make it pass  
3. Add yourself to ``docs/credits.rst``

Changelog Entry Format
~~~~~~~~~~~~~~~~~~~~~

Add your entry under the appropriate section in ``CHANGES.rst``:

- **Minor changes:** For bug fixes, small improvements, refactoring
- **Breaking changes:** For changes that break existing API
- **New features:** For new functionality

Example::

    Minor changes:
    
    - Fix issue with timezone parsing in special cases. See `Issue XXX <link>`_.

Setup for Development
---------------------

If you would like to setup icalendar to
contribute changes, the `Installation Section
<https://icalendar.readthedocs.io/en/latest/install.html>`_
should help you further.
