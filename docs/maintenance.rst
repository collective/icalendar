Maintenance
===========

The goal of this section is to make sure that the ``icalendar`` library receives a
clear maintenance structure with it that is transparent.


Maintainers
-----------

Currently, the maintainers are

- `@geier <https://github.com/geier>`_
- `@jacadzaca <https://github.com/jacadzaca>`_
- `@niccokunzmann <https://github.com/niccokunzmann>`_

Maintainers need this:

- ``Admin`` access to the `repository <https://github.com/collective/icalendar>`_.
    These can be enabled by a current maintainer or an GitHub organisation administrator
    in the `settings <https://github.com/collective/icalendar/settings/access>`_.
- ``Maintainer`` or ``Owner`` access to the `PyPI project  <https://pypi.org/project/icalendar/>`_.
    The new maintainer needs a PyPI account for this with Two Factor Authentication (2FA) enabled
    because ``icalendar`` is a critical project on PyPI.
    The access can be given in the `collaboration Section <https://pypi.org/manage/project/icalendar/collaboration/>`_ on PyPI.
- ``Maintainer`` access to the `Read The Docs project <https://readthedocs.org/projects/icalendar/>`_.
    This can be given by existing maintainers listed on the project's page.
    TODO: link to the settings
- ``PyPI environment access for GitHub Actions`` grant new releases from tags.
    This access can be granted in `Settings → Environments → PyPI <https://github.com/collective/icalendar/settings/environments/674266024/edit>`__
    by adding the GitHub username to the list of "Required Reviewers".


Contributors
------------

Contributors here are people with write access to the repository.
We want to have as many knowledgeable people with write access taking responsibility as possible for these reasons:

- a constant flow of fixes and new features
- better code review
- lower bus factor and backup
- future maintainers

Nobody should merge their own pull requests.
If you like to review or merge pull requests of other people and you have shown that you know how to contribute,
you can ask for becoming a contributor or a maintainer asks you if you would like to become one.

New Releases
------------

This explains how to create a new release on `PyPI  <https://pypi.org/project/icalendar/>`_.

Since contributors and maintainers have write access the the repository, they can start the release process.
However, only people with ``PyPI environment access for GitHub Actions`` can approve an automated release to PyPI.


1. Check that the ``CHANGES.rst`` is up to date with the `latest merged pull requests <https://github.com/collective/icalendar/pulls?q=is%3Apr+is%3Amerged>`__
   and the version you want to release is correctly named.
2. Change the ``__version__`` variable in

   - the ``src/icalendar/__init__.py`` file and 
   - in the ``docs/install.rst`` file (look for ``icalendar.__version__``)
3. Create a commit on the ``release`` branch (or equivalent) to release this version.

   .. code-block:: bash

       git checkout master
       git pull
       git checkout -b release master
       git add CHANGES.rst src/icalendar/__init__.py docs/install.rst
       git commit -m"version 5.0.0"

4. Push the commit and `create a pull request <https://github.com/collective/icalendar/compare?expand=1>`__
   Here is an `example pull request #457 <https://github.com/collective/icalendar/pull/457>`__.

   .. code-block:: bash

       git push -u origin release

5. See if the `CI-tests <https://github.com/collective/icalendar/actions>`_ are running on the pull request.
   If they are not running, no new release can be issued.
   If the tests are running, merge the pull request.
6. Clean up behind you!

   .. code-block:: bash

       git checkout master
       git pull
       git branch -d release
       git push -d origin release

7. Create a tag for the release and see if the `CI-tests`_ are running.

   .. code-block:: bash

       git checkout master
       git pull
       git tag v5.0.0
       git push upstream v5.0.0 # could be origin or whatever reference

8. Once the tag is pushed and its `CI-tests`_ are passing, maintainers will get an e-mail::

       Subject: Deployment review in collective/icalendar

       tests: PyPI is waiting for your review

9. If the release is approved by a maintainer. It will be pushed to `PyPI`_.
   If that happens, notify the issues that were fixed about this release.
10. Copy this to the start of ``CHANGES.rst``::

       5.0.2 (unreleased)
       ------------------
       
       Minor changes:
       
       - ...
       
       Breaking changes:
       
       - ...
       
       New features:
       
       - ...
       
       Bug fixes:
       
       - ...

11. Push the new CHANGELOG so it is used for future changes.

   .. code-block:: bash

       git checkout master
       git pull
       git add CHANGES.rst
       git commit -m"Add new CHANGELOG section for future release
       
       See https://icalendar.readthedocs.io/en/latest/maintenance.html#new-releases"
       git push upstream master # could be origin or whatever reference

Links
-----

This section contains useful links for maintainers and contributors:

- `Future of icalendar, looking for maintainer #360 <https://github.com/collective/icalendar/discussions/360>`__
- `Comment on the Plone tests running with icalendar <https://github.com/collective/icalendar/pull/447#issuecomment-1277643634>`__




