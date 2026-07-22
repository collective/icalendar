==========
Contribute
==========

This guide describes how to contribute to icalendar.

A key purpose around icalendar is to foster a warm and welcoming space for people to learn, grow, and contribute.
Contributors in the icalendar community find joy in working with other people and raising them up to contribute again and improve.

People in the icalendar community strive to uphold the spirit of the Python Calendaring Ecosystem's `Code of Conduct <https://pycal.org/code-of-conduct/>`_.
You are invited to read it to help you decide whether you would enjoy being a part of the icalendar community.

Examples of how to contribute
-----------------------------

-   Report security issues per the `Security Policy <https://github.com/collective/icalendar/blob/main/SECURITY.md>`_.
-   Report all other issues in the `issue tracker <https://github.com/collective/icalendar/issues>`_.
-   Comment on and resolve issues.
-   Triage open issues and `pull requests <https://github.com/collective/icalendar/pulls>`_.
-   Review, comment on, and make suggestions to change a pull request.
    See the GitHub documentation `Reviewing proposed changes in a pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request>`_.
-   Submit pull requests from your fork of the icalendar repository.
-   Extend the :doc:`documentation/index`.
-   Create or comment on a topic in `Discussions <https://github.com/collective/icalendar/discussions>`_.
-   Write a blog post about icalendar.
-   Share announcements on social media from :doc:`core contributors <credits>` to icalendar.
-   Sponsor development of icalendar through `Open Collective <https://opencollective.com/python-icalendar>`_.


.. _first-time-contributors:

First-time contributors
-----------------------

Contributions to icalendar from people new to icalendar are welcome.

Like most free and open source software, icalendar promotes the "free" part, meaning freedom or liberty.

-   You're free to start work on issues without asking.
-   You're free to ask questions to clarify the scope of work before you start.
-   We don't assign issues.
-   Free other contributors from duplicating your effort by opening a pull request as soon as you can.

For people participating in programs to encourage first-time contributions, including `Hacktoberfest <https://hacktoberfest.com/>`_, `Good First Issue <https://goodfirstissue.dev/language/python#repo-2222138>`_, and `Up For Grabs <https://up-for-grabs.net/#/filters?tags=ical%2Cicalendar%2Cics%2Crfc5545>`_, you must comply with their terms and conditions to receive their recognition or rewards.
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
Pull request reviewers want to train people, not AI.
As such, we take a strong stance against artificial intelligence (AI) abuse.

Contributors to icalendar must follow icalendar's AI policy as described in this section.


.. _responsible-ai-use:

Responsible AI use
``````````````````

You may responsibly use AI as a tool to draft a pull request.
That means you must comply with :ref:`pull-request-requirements` and follow the Python Calendaring Ecosystem's `Code of Conduct <https://pycal.org/code-of-conduct/>`_.

If you use AI in your work:

-   Before you begin work, you must open an issue per :ref:`issue-requirements`.
-   In your git commit messages, you must specify both (1) which AI model and version you used, and (2) how you used it, by either including the prompts and interactions you used or summarizing them.
    See the example commit message below.

    ..  code-block:: text

        Author: Parker Programmer with CodeLLM-3.4 pp@example.org
        Date: Sun Jan 18 10:52:08 2026
        Generate compliance tests
        Prompt: Generate tests for compliance with RFC123 messages.
        Output: (this commit)

    You can automate this by using the :program:`ai-prompt-auto-commit` pre-commit hook.
    See :ref:`AI prompt automation <pre-commit-ai-prompts>` for setup instructions.
-   You must disclose that you used AI in your change log entry.
    This may be a brief disclosure, not as detailed as the git commit messages, such as, "I used AI to assist me with this change."
-   You must take responsibility for the output, including reviewing and validating the output for accuracy and ensuring it resolves an issue.
-   You must check the AI's terms of use, and ensure that outputs are not reconstructed from copyrighted sources.
-   You are expected to understand and be able to explain design and code decisions.
-   You shall be held accountable for your AI-generated content.


AI abuse
````````

You may not abuse AI to generate a pull request that is disruptive to the icalendar community or does not adhere to :ref:`responsible-ai-use` described in the previous subsection.
Examples of such abuse and irresponsible use include the following actions.

-   You claim no responsibility for the output of AI generated content.
-   Your pull request demonstrates no understanding or thought whatsoever to solve an issue.
-   Your pull request plagiarizes copyrighted or other material to which you have no legal claim.
-   You ignore or don't respond to feedback.
-   The GitHub account is itself an AI agent.


Report suspected violations
```````````````````````````

To report a suspected violation of this AI policy, see the `Reporting an issue <https://pycal.org/code-of-conduct/#reporting-an-issue>`_ section in the Python Calendaring Ecosystem's Code of Conduct.
The maintainers will investigate and collect information from various sources, including but not limited to the use of automated GitHub workflows to identify suspected AI use.
The maintainers may close pull requests without providing feedback that they deem to be spam, AI slop, abuse, or that do not comply with :ref:`pull request requirements <pull-request-requirements>`.
The maintainers may also take further action, including suspend, ban, or report GitHub users, as described in Python Calendaring Ecosystem's `Code of Conduct <https://pycal.org/code-of-conduct/>`_.


.. _issue-requirements:

Issue requirements
------------------

An issue should precede a pull request.

When `creating a new issue <https://github.com/collective/icalendar/issues/new/choose>`_, you'll be presented with an issue selector.
Follow the templates guidance as much as practical.

It might be helpful to include an iCalendar file to help reproduce your issue and to use in a test to ensure a bug fix actually resolves your issue.
To remove private information from an iCalendar file, use :program:`icalendar-anonymizer`, either through its `website <https://icalendar-anonymizer.com/>`_ or install it locally.
See icalendar-anonymizer's `Installation <https://docs.icalendar-anonymizer.com/latest/installation.html>`_ and documentation for details.

Anyone may comment on an issue.
Discussion of the issue helps collaborators understand its importance and how to resolve it.

.. _pull-request-requirements:

Pull request requirements
-------------------------

When submitting your pull request, complete the description template on GitHub, and ensure you have met the following requirements.

#.  In your pull request description, link to relevant issues.
#.  Add a change log entry as described in :ref:`change-log`.
    This is required and enforced by GitHub checks.
#.  Add a test which proves your fix and passes.
#.  Run all tests to ensure your changes don't break any existing functionality.
#.  :doc:`Add or edit documentation <documentation/index>`, both as docstrings to be rendered in the :doc:`API reference documentation <../reference/api/icalendar>` and narrative documentation, as necessary.

The maintainers may close pull requests without providing feedback that they deem to be spam, AI slop, abuse, or that do not comply with pull request requirements.
The maintainers may also take further action, including suspend, ban, or report GitHub users, as described in Python Calendaring Ecosystem's `Code of Conduct <https://pycal.org/code-of-conduct/>`_.


.. _change-log:

Change log requirements
-----------------------

This section describes how to write a change log entry that satisfies the requirements of its :ref:`file name <change-log-file-name>` according to :ref:`types <change-log-types>` and which :ref:`summarizes changes <write-a-good-change-log-entry-label>` in your contribution, including compliance with icalendar's :ref:`responsible-ai-use` policy.

.. _change-log-file-name:

Change log entry file name
``````````````````````````

To create a change log entry or news item, create a file in the :file:`news` directory, located in the root of the package.

..  important::

    Never edit a change log entry that you didn't create.

The change log entry's format must be ``#.type``, where ``#`` is the referenced GitHub issue or pull request number, ``.`` is the literal extension delimiter, and ``type`` is one of the following strings described in the next section, :ref:`change-log-types`

To avoid a filename conflict with an existing file or another pull request for the same issue number, append a period (``.``) and an integer to the filename, incrementing it as needed to make the entire filename unique.

..  code-block:: text

    1158.documentation
    1158.documentation.1
    1158.documentation.2

For orphan change log entries—that is, those that don't need to be linked to any issue ID or other identifier—start the file name with ``+``.
The content will still be included in the change log, at the end of the category corresponding to the file extension.

..  code-block:: text

    +anything.bugfix

.. note::

    icalendar uses `towncrier <https://pypi.org/project/towncrier/>`_ to automatically update the :doc:`../reference/changelog` from entries stored in the :file:`/news` directory at the root of the project.
    It generates links to the issue numbers and organizes the change log entries according to their filename issue numbers and types for each release.


..  _change-log-types:

Change log types
~~~~~~~~~~~~~~~~

``breaking``
    For changes that break the existing API.

``removal``
    For removals and deprecations.

``feature``
    For new functionality.

``bugfix``
    For bug fixes and error corrections.

``security``
    For security fixes.
    These must go through the `security report protocol <https://github.com/collective/icalendar/blob/main/SECURITY.md>`_.

``documentation``
    For changes to the documentation, docstrings, spelling dictionary, or any other documentation matter.

``deps``
    For changes to project dependencies.

``internal``
    For internal changes, such as issue templates.

``chore``
    For routine tasks that shouldn't be published, but will satisfy the checker for the presence of a change log entry.


.. _write-a-good-change-log-entry-label:

Write a good change log entry
`````````````````````````````

.. important::

    These change log entries become narrative documentation.

The content of this file must include the following.

-   A brief message that summarizes the changes in your contribution.
-   Use :ref:`reStructuredText markup <markup-examples>` to link to relevant RFCs, API usage, and other references.
-   A brief disclosure of AI use, per icalendar's :ref:`responsible-ai-use` policy, if applicable.
-   An attribution to yourself, in the format of ``@github_username``, at the end of the entry.

You can write a good change log entry with the following guidance.

-   Use a narrative format, in the past tense, proper English spelling and grammar, and inline markup as needed.
-   Write your change log entry for its appropriate audience.

    -   Most entries should address *users* of the software.
    -   An entry for a change to a public API should address *developers*.

-   If you fix a bug, write what was broken and is now fixed.
    You should not write *how* you fixed it.
-   If you add or change a feature or public API, write a summary of previous behavior, what it does now, and how to use it.
-   Refer to narrative documentation as needed.

The following text is an example of a good change log entry, placed inside :file:`/news/1360.feature`.

..  code-block:: rst

    Created a :meth:`~icalendar.prop.recur.weekday.vWeekday.ical_value` property for the :class:`~icalendar.prop.recur.weekday.vWeekday` component, mirroring the existing pattern on :class:`~icalendar.prop.boolean.vBoolean`. @mvanhorn

The following would be a poor change log entry.

..  code-block:: rst

    Fix #123456 by chaning config of file [did_not_read_this_guide]


Set up for development
----------------------

If you would like to set up icalendar to contribute changes, see :doc:`development`.



.. toctree::
    :hidden:

    documentation/index
    development
    code-of-conduct
    credits
    maintenance
