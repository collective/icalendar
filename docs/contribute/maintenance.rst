===========
Maintenance
===========

This chapter describes the maintenance structure of icalendar.

icalendar Maintainers
---------------------

Currently the maintainers are the following people.

- `@geier <https://github.com/geier>`_
- `@jacadzaca <https://github.com/jacadzaca>`_
- `@niccokunzmann <https://github.com/niccokunzmann>`_

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
    This Google Group is used for managing `Code of Conduct <https://github.com/collective/icalendar/blob/main/CODE_OF_CONDUCT.md>`_ infringement reports.
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
        -   `OSS Fuzz Integration - Issue 562 <https://github.com/collective/icalendar/issues/562>`_
    

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


New releases
------------

This section explains how to create a new release on `PyPI <https://pypi.org/project/icalendar/>`_.

Since collaborators and maintainers have write access to the repository, they can start the release process.
However, only people with ``Environments/Configure PyPI`` access can approve an automated release to PyPI.

#.  Check that the file :file:`CHANGES.rst` is up to date with the `latest merged pull requests <https://github.com/collective/icalendar/pulls?q=is%3Apr+is%3Amerged>`_, and the version you want to release is correctly named.

#.  Set an environment variable to use in subsequent commands during the release process.

    .. code-block:: shell

        export VERSION=7.0.0

#.  If you want to cut a new release of a stable version, then in the ``main`` or development branch, update :file:`docs/_static/version-switcher.json` to match that version.

#.  Create a commit on the ``release`` branch (or equivalent) to release this version.

    .. code-block:: shell

        git checkout main
        git pull
        git checkout -b release-$VERSION main
        git add CHANGES.rst docs/_static/version-switcher.json
        git commit -m"version $VERSION"

#.  Push the commit and `create a pull request <https://github.com/collective/icalendar/compare?expand=1>`_.
    Here is an `example pull request #457 <https://github.com/collective/icalendar/pull/457>`_.

    .. code-block:: shell

        git push -u origin release-$VERSION

#.  See if the `CI-tests <https://github.com/collective/icalendar/actions>`_ are running on the pull request.
    If they are not running, no new release can be issued.
    If the CI passes, merge the pull request.

#.  Clean up behind you!

    .. code-block:: shell

        git checkout main
        git pull
        git branch -d release-$VERSION
        git push -d origin release-$VERSION

#.  Create a tag for the release and see if the `CI-tests`_ are running.

    .. code-block:: shell

        git checkout main
        git pull
        git tag "v$VERSION"
        git push upstream "v$VERSION" # could be origin or whatever reference

    .. warning::

        Once a tag is pushed to the repository, it must not be re-tagged or deleted.
        This creates issues for downstream repositories.
        See `Issue 1033 <https://github.com/collective/icalendar/issues/1033>`_.

#.  Once the tag is pushed and its `CI-tests`_ are passing, maintainers will get an e-mail:

    .. code-block:: text

        Subject: Deployment review in collective/icalendar

        tests: PyPI is waiting for your review

#.  If the release is approved by a maintainer, it will be pushed to `PyPI`_.
    If that happens, notify the issues that were fixed about this release.
#.  Copy this to the start of ``CHANGES.rst``.

    .. code-block:: text

       7.0.0 (unreleased)
       ------------------

       Minor changes
       ~~~~~~~~~~~~~

       - ...

       Breaking changes
       ~~~~~~~~~~~~~~~~

       - ...

       New features
       ~~~~~~~~~~~~

       - ...

       Bug fixes
       ~~~~~~~~~

       - ...

#.  Push the new ``CHANGELOG`` so it is used for future changes.

    .. code-block:: shell

        git checkout main
        git pull
        git add CHANGES.rst
        git commit -m "Add new CHANGELOG section for future release"
        git push upstream main # could be origin or whatever reference

Links
-----

This section contains useful links for maintainers and collaborators.

-   `Future of icalendar, looking for maintainer #360 <https://github.com/collective/icalendar/discussions/360>`_
-   `Comment on the Plone tests running with icalendar <https://github.com/collective/icalendar/pull/447#issuecomment-1277643634>`_


Updating Python versions
------------------------

When adding support for a new Python version, or removing support for an old one, the following files need to be updated:

:file:`.github/workflows/tests.yml`
    Add or remove the Python version from the test matrix.
:file:`tox.ini`
    Update the ``envlist`` to include or remove the Python version.
:file:`pyproject.toml`
    Update the ``requires-python`` line and the ``classifiers`` list.
:file:`README.rst`
    Update the compatibility information.
:file:`docs/maintenance.rst`
    Update this list if any new files need to be modified.

Remember to write tests that completely cover the changes, and update any documentation that mentions supported Python versions.
