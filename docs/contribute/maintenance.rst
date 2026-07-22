===========
Maintenance
===========

This chapter describes the maintenance structure of icalendar.

icalendar Maintainers
---------------------

Currently the maintainers are the following people.

.. include:: ../_include/maintainers.inc

Maintainers need the following permissions.

``Admin`` access to the `repository <https://github.com/collective/icalendar>`_.
    These can be enabled by a current maintainer or a GitHub organization administrator in the `settings <https://github.com/collective/icalendar/settings/access>`_.
``Maintainer`` or ``Owner`` access to the `PyPI project <https://pypi.org/project/icalendar/>`_.
    Each owner and maintainer needs a PyPI account.
    All PyPI accounts require two-factor authentication (2FA) enabled.
    Owners can invite either new owners or maintainers in the `collaboration Section <https://pypi.org/manage/project/icalendar/collaboration/>`_ on PyPI.
``Maintainer`` access to the `Read the Docs project <https://app.readthedocs.org/projects/icalendar/>`_.
    Existing maintainers can invite another maintainer through the `Maintainers <https://app.readthedocs.org/dashboard/icalendar/users/create/>`_ page.
``Environments/Configure PyPI`` access for GitHub Workflows to grant new releases from tags.
    Organization owners and repository administrators can grant this access in :menuselection:`Settings --> Environments --> PyPI`, or at https://github.com/collective/icalendar/settings/environments/674266024/edit, by adding their GitHub username to the list of :guilabel:`Required Reviewers`.
``Owner`` or ``Manager`` access to ``icalendar-coc@googlegroups.com``
    This Google Group is used for managing `Code of Conduct <https://pycal.org/code-of-conduct/>`_ infringement reports.
    ``Manager``\ s may manage and moderate messages, whereas ``Owner``\ s may also manage members.
    Management is performed through `Google Groups icalendar-coc settings <https://groups.google.com/g/icalendar-coc/settings>`_.
``Registered`` access to the `OSS Fuzz issue tracker <https://issues.oss-fuzz.com/issues?q=icalendar>`_ for icalendar.
    icalendar contributors use this issue tracker for managing :doc:`../how-to/fuzz-testing` issues that arise from time to time.
    New issues do not get immediately disclosed to the public, and require that you register with a Google Account.
    Add your Google Account's email address to `google/oss-fuzz <https://github.com/google/oss-fuzz/blob/master/projects/icalendar/project.yaml>`_, and create a pull request, to request the following access:

    -   instant notification about fuzzing errors
    -   undisclosed fuzzing issues

    Existing issues will be disclosed after some time to the public.

    .. seealso::

        -   `Discussion about how to be added to OSS Fuzz <https://github.com/collective/icalendar/pull/574#issuecomment-1790554766>`_
        -   :issue:`562`
Maintainer in :file:`pyproject.toml`
    Maintainers should be mentioned with or without email address in the :file:`pyproject.toml` file's `maintainers' section <https://github.com/collective/icalendar/blob/7ca9db18c0847d1530520e01baf75f8ab8f4fa06/pyproject.toml#L32>`_.

Collaborators
-------------

Collaborators have write access to the repository.
As a collaborator, you can

-   merge pull requests,
-   initiate a new release, and
-   become a :ref:`code-owner`.

The maintainers of icalendar want to have as many knowledgeable people with write access taking responsibility as possible for these reasons:

-   a constant flow of fixes and new features
-   better code review
-   lower bus factor and backup
-   future maintainers

Nobody should merge their own pull requests.
If you like to review or merge pull requests of other people and you have shown that you know how to contribute, you can ask to become a collaborator.
A maintainer may ask if you would like to become one.


.. _code-owner:

Code owner
----------

A code owner is a type of collaborator or maintainer who is responsible for a specific part of the code.
Code owners are automatically requested for review when someone opens a pull request that modifies code that they own.

You may ask, or be invited, to become a code owner as part of becoming a collaborator or maintainer.
When doing so, you or the inviter may submit a pull request to update the :file:`.github/CODEOWNERS` file.

.. seealso:: `About code owners <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners>`_

Release versions
----------------

..  seealso:: 
    :doc:`/reference/versions-branches`

New releases
------------

This section explains how to create a new release on `PyPI <https://pypi.org/project/icalendar/>`_.

Its examples were used for the 7.0.0 release of icalendar, a major release.
Adjust the examples for the current release as needed.

Since collaborators and maintainers have write access to the repository, they can start the release process.
However, only people with ``Environments/Configure PyPI`` access can approve an automated release to PyPI.

#.  Update the Windows to Olson mapping in the :mod:`~icalendar.timezone.windows_to_olson` module.

    ..  code-block:: shell

        make wo

    If there are any changes to the module, then open a pull request and merge it.

#.  Set an environment variable to use in subsequent commands during the release process.

    .. code-block:: shell

        export VERSION=7.0.0

#.  Update the ``main`` branch.

    .. code-block:: shell

        git checkout main
        git pull

#.  If you'll create a new *major* release, update :file:`.github/workflows/tests.yml` to include the new release branch in the list of branches that trigger the CI tests.

    ..  code-block:: yaml
        :emphasize-lines: 4

        push:
          branches:
          - main
          - 7.x
          tags:
          - v*

    .. _hide-version-warning-banner:

#.  Hide the version warning banner on the "stable" version on Read the Docs.
    Update the Sphinx configuration file :file:`docs/conf.py`, which you'll commit and tag.
    Then Read the Docs will recognize the highest version tag as the "stable" version.

    ..  note::

        Toward the end of this process, you'll revert this setting on ``main``, so that the "latest" version on Read the Docs continues to display the version warning banner.

    .. code-block:: python

        html_theme_options = {
            # ...
            "show_version_warning_banner": False,

#.  Update the change log :file:`CHANGES.rst` with the change log entries in :file:`/news` using `towncrier <https://pypi.org/project/towncrier/>`_.

    ..  code-block:: shell

        make changes

#.  Add the changes, create a commit on the ``main`` branch, and push the changes to prepare a release of this version.

    .. code-block:: shell

        git add CHANGES.rst news/
        git add .github/workflows/tests.yml  # Only for a new major release
        git commit -m"version $VERSION"
        git push  # to collective/icalendar

#.  See if the `CI tests <https://github.com/collective/icalendar/actions>`_ are running on the commit.
    If they are not running, no new release can be issued.
    If the CI passes, go ahead.

#.  Create a tag for the release on its release branch ``*.x``, push, and make sure the `CI tests`_ are running.

    a.  First, make sure you're on the ``main`` branch and it's current, in case someone else updated ``main`` while tests ran.

        .. code-block:: shell

            git checkout main
            git pull

    #.  Next, depending on the release type, do one of the following.

        -   For a major release, create a new branch, and check it out.

            .. code-block:: shell

                git switch -c 7.x

        -   For a minor or patch release, check out the existing branch, and update it.

            .. code-block:: shell

                git checkout 7.x
                git pull

    #.  Next, merge ``main`` into the release branch.

        .. code-block:: shell

            git merge main

    #.  Next, push changes upstream, changing the command according to the release type.

        -   For a major release, push, create, and track the upstream branch.

            .. code-block:: shell

                git push -u upstream 7.x  # to collective/icalendar

        -   For a minor or patch release, just push.

            .. code-block:: shell

                git push  # to collective/icalendar

    #.  Next create a tag, and push the tag.

        .. code-block:: shell

            git tag "v$VERSION"
            git push upstream "v$VERSION" # to collective/icalendar

        .. warning::

            Once a tag is pushed to the repository, it must not be re-tagged or deleted.
            This creates issues for downstream repositories.
            See :issue:`1033`.

#.  Once the tag is pushed and its `CI tests`_ pass, check the `GitHub Actions <https://github.com/collective/icalendar/actions>`_, and wait for maintainers to get an email:

    .. code-block:: text

        Subject: Deployment review in collective/icalendar

        tests: PyPI is waiting for your review

#.  If the release is approved by a maintainer, it will be pushed to `PyPI`_.
    Don't wait for that, continue.

#.  Update the version switcher file :file:`docs/_static/version-switcher.json`.

    .. note::

        This file is configured in :file:`docs/conf.py` on *all* branches to use the version on the ``main`` branch, which is "latest" on Read the Docs.

        ..  code-block:: python

            json_url = "https://icalendar.readthedocs.io/en/latest/_static/version-switcher.json"

    The following examples were used for the 7.0.0 release.

    a.  Check out the ``main`` branch and update it.

        ..  code-block:: shell

            git checkout main
            git pull

    #.  When cutting a new *major* release version, update :file:`docs/_static/version-switcher.json` to match that version.

        -   Duplicate the second previous major version stanza and renumber it to the first previous version.
            In other words, duplicate the ``5.x`` stanza, and renumber the copy to ``6.x``.

            .. code-block:: json

                {
                    "version": "6.x",
                    "url": "https://icalendar.readthedocs.io/en/6.x/"
                },

        -   Next, edit the array item for the previous version to reflect the current major release.

            .. vale off

            .. code-block:: json
                :emphasize-lines: 2-3

                {
                    "name": "7.x (stable)",
                    "version": "v7.0.0",
                    "url": "https://icalendar.readthedocs.io/en/stable/",
                    "preferred": "true"
                },

            .. vale on

    #.  When cutting a *minor* or *patch* release version, update :file:`docs/_static/version-switcher.json` to match that version's tag name.

        .. vale off

        .. code-block:: json
            :emphasize-lines: 2-3

            {
                "name": "7.x (stable)",
                "version": "v7.0.1",
                "url": "https://icalendar.readthedocs.io/en/stable/",
                "preferred": "true"
            },

        .. vale on

    #.  For all releases, add, commit, and push the changes.

        .. code-block:: shell

            git add docs/_static/version-switcher.json
            git commit -m "Update version switcher for $VERSION"
            git push  # to collective/icalendar

#.  Revert the change in the :ref:`earlier step <hide-version-warning-banner>` by updating the Sphinx configuration file :file:`docs/conf.py` to show the version warning banner on the ``main`` branch, which is "latest" on Read the Docs.

    ..  code-block:: shell

        git checkout main
        git pull

    ..  code-block:: python

        html_theme_options = {
            # ...
            "show_version_warning_banner": True,

    ..  code-block:: shell

        git add docs/conf.py
        git commit -m "Restore version warning banner for 'latest' on Read the Docs"
        git push  # to collective/icalendar

#.  If you cut a new *major* release version, update the Sphinx configuration file :file:`docs/conf.py` on the *previous* numbered major release branch to show the version warning banner.
    For example, when releasing 7.0.0, checkout ``6.x``, and update it as shown.

    .. code-block:: shell

        git checkout 6.x
        git pull

    .. code-block:: python

        html_theme_options = {
            # ...
            "show_version_warning_banner": True,

    ..  code-block:: shell

        git add docs/conf.py
        git commit -m "Show version warning banner for previous major version 6.x on Read the Docs"
        git push  # to collective/icalendar

#.  Manually trigger the "latest" version on `Read the Docs <https://app.readthedocs.org/projects/icalendar/>`_.
    To the right in the row for "latest," click the ellipsis :guilabel:`…`, and from the pop-up menu select :guilabel:`Rebuild version`.

#.  Add a comment to each of the issues mentioned in the new release.
    Example:

    .. code-block:: text

        This is included in v7.0.0.


Links
-----

This section contains useful links for maintainers and collaborators.

-   To remove private information from an iCalendar file for bug reports, use `icalendar-anonymizer <https://github.com/pycalendar/icalendar-anonymizer>`_ either through its `website <https://icalendar-anonymizer.com/>`_ or `install it locally <https://docs.icalendar-anonymizer.com/latest/installation.html>`_.
-   `Python Calendaring Ecosystem <https://pycal.org/>`_
-   `Future of icalendar, looking for maintainer #360 <https://github.com/collective/icalendar/discussions/360>`_
-   `Comment on the Plone tests running with icalendar <https://github.com/collective/icalendar/pull/447#issuecomment-1277643634>`_


Updating Python versions
------------------------

When adding support for a new Python version, or removing support for an old one, the following files need to be updated:

:file:`.github/workflows/tests.yml`
    Upgrade Python versions.
:file:`.github/workflows/*.py`
    Add or remove the Python version from the test matrix.
:file:`tox.ini`
    Update the ``envlist`` to include or remove the Python version.
:file:`pyproject.toml`
    Update the ``requires-python`` line and the ``classifiers`` list.
:file:`docs/reference/versions-branches.rst`
    Update the compatibility information.
:file:`docs/maintenance.rst`
    Update this list if any new files need to be modified.
`Branch Protection Rules <https://github.com/collective/icalendar/settings/branch_protection_rules>`_
    Update the branch protection rules so that they match the required test names.

Remember to write tests that completely cover the changes, and update any documentation that mentions supported Python versions.
