============
Contributing
============

This guide describes how to contribute to icalendar.

Examples of how to contribute
-----------------------------

-   Report issues in the `issue tracker <https://github.com/collective/icalendar/issues>`_.
-   Submit pull requests from your fork of the icalendar repository.
-   Extend the :doc:`documentation`.
-   Sponsor development of icalendar through `Open Collective <https://opencollective.com/python-icalendar>`_.


.. _first-time-contributors:

First-time contributors
-----------------------

Contributions to icalendar from people new to icalendar are welcome.

For people participating in programs to encourage first-time contributions, including `Hacktoberfest <https://hacktoberfest.com/>`_ and `Up For Grabs <https://up-for-grabs.net/#/filters?names=478>`_, you must comply with its terms and conditions to receive its recognition or rewards.
Accordingly, you may request of the maintainers in your pull request that you would like recognition for your contribution.

You may responsibly use artificial intelligence (AI) as a tool to draft a pull request.
That means you must comply with :ref:`pull-request-requirements`.

.. seealso::

    Find open issues.

    .. grid:: 1 2 3 4

        .. grid-item::

            .. button-link:: https://github.com/collective/icalendar/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22
                :color: primary
                :shadow:

                Good First Issue

        .. grid-item::

            .. button-link:: https://github.com/collective/icalendar/issues?q=is%3Aissue%20state%3Aopen%20label%3Ahacktoberfest
                :color: warning
                :shadow:

                Hacktoberfest


.. _pull-request-requirements:

Pull request requirements
-------------------------

Before submitting your pull request, ensure you have met the following requirements.

#.  Add a changelog entry to :file:`CHANGES.rst`.
    This is required and enforced by GitHub checks.
    See :ref:`change-log` for details.
#.  Add a test which proves your fix and passes.
#.  Run all tests to ensure your changes don't break any existing functionality.
#.  :ref:`Add or edit documentation <documentation-prerequisites>`_, both as docstrings to be rendered in the API documentation and narrative documentation, as necessary.
#.  Add yourself to :file:`docs/credits.rst`, if you haven't already done so.

The maintainers may close pull requests without providing feedback that they deem to be spam, AI slop, abuse, or that do not comply with pull request requirements.
The maintainers may also take further action, including suspend, ban, or report GitHub users.


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

    documentation
    development
    credits
    maintenance
