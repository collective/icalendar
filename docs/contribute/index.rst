============
Contributing
============

This guide describes how to contribute to icalendar.

Examples of how to contribute
-----------------------------

-   Report issues in the `issue tracker <https://github.com/collective/icalendar/issues>`_.
-   Comment on and resolve issues.
-   Submit pull requests from your fork of the icalendar repository.
-   Extend the :doc:`documentation`.
-   Sponsor development of icalendar through `Open Collective <https://opencollective.com/python-icalendar>`_.


.. _first-time-contributors:

First-time contributors
-----------------------

Contributions to icalendar from people new to icalendar are welcome.

For people participating in programs to encourage first-time contributions, including `Hacktoberfest <https://hacktoberfest.com/>`_ and `Up For Grabs <https://up-for-grabs.net/#/filters?names=478>`_, you must comply with its terms and conditions to receive its recognition or rewards.
Accordingly, you may request of the maintainers in your pull request that you would like recognition for your contribution.

.. seealso::

    Find open issues.

    .. grid:: 1 2 3 4

        .. grid-item::

            .. button-link:: https://github.com/collective/icalendar/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22
                :color: primary
                :shadow:

                Good First Issue

        .. grid-item::

            .. button-link:: https://github.com/collective/icalendar/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22doc%22
                :color: success
                :shadow:

                Documentation

        .. grid-item::

            .. button-link:: https://github.com/collective/icalendar/issues?q=is%3Aissue%20state%3Aopen%20label%3Ahacktoberfest
                :color: warning
                :shadow:

                Hacktoberfest


.. _artificial-intelligence-policy:

Artificial intelligence policy
------------------------------

We want to protect the joy, goodwill, and volunteer time of the maintainers and contributors of icalendar.
As such, we take a strong stance against artificial intelligence (AI) abuse.

Contributors to icalendar must follow icalendar's AI policy as described in this section.


Responsible AI use
``````````````````

You may responsibly use AI as a tool to draft a pull request.
That means you must comply with :ref:`pull-request-requirements` and follow icalendar's `Code of Conduct <https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md>`_.
It also means that you must take responsibility for the output, including reviewing and validating the output for accuracy and ensuring it resolves an issue.
You shall be held accountable for your AI-generated content.


AI abuse
````````

You may not abuse AI to generate a pull request that is disruptive to the icalendar community.
Examples of such abuse include the following actions.

-   You claim no responsibility for the output of AI generated content.
-   Your pull request demonstrates no understanding or thought whatsoever to solve an issue.
-   Your pull request plagiarizes copyrighted or other material to which you have no legal claim.
-   You ignore or don't respond to feedback.


Report suspected violations
```````````````````````````

To report a suspected violation of this AI policy, see the `Enforcement <https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md#enforcement>`_ section in the Code of Conduct.
The maintainers may close pull requests without providing feedback that they deem to be spam, AI slop, abuse, or that do not comply with :ref:`pull request requirements <pull-request-requirements>`.
The maintainers may also take further action, including suspend, ban, or report GitHub users, as described in icalendar's `Code of Conduct <https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md>`_.


.. _pull-request-requirements:

Pull request requirements
-------------------------

Before submitting your pull request, ensure you have met the following requirements.

#.  Add a changelog entry to :file:`CHANGES.rst`.
    This is required and enforced by GitHub checks.
    See :ref:`change-log` for details.
#.  Add a test which proves your fix and passes.
#.  Run all tests to ensure your changes don't break any existing functionality.
#.  :doc:`Add or edit documentation <documentation>`, both as docstrings to be rendered in the :doc:`API reference documentation <../reference/api/icalendar>` and narrative documentation, as necessary.
#.  Add yourself to :file:`docs/credits.rst`, if you haven't already done so.

The maintainers may close pull requests without providing feedback that they deem to be spam, AI slop, abuse, or that do not comply with pull request requirements.
The maintainers may also take further action, including suspend, ban, or report GitHub users, as described in icalendar's `Code of Conduct <https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md>`_.


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
    code-of-conduct
    credits
    maintenance
