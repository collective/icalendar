Maintenance
===========

The goal of this section is to make sure that the ``icalendar`` library receives a
clear maintenance structure with it that is transparent.


Maintainers
-----------

Currently, the maintainers are

- `@geier <https://github.com/geier>`_
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

This explains how to create a new release on PyPI.
You will need write access to the `PyPI project`_.

1. Check that the ``CHANGES.rst`` is up to date with the latest merges and the version you want to release is correctly named.
2. Change the ``__version__`` variable in the ``src/icalendar/__init__.py`` file.
3. Create a commit on the ``master`` branch to release this version.

    .. code-block:: bash

        git checkout master
        git commit -am"version 5.0.0a2"
4. Push the commit and see if the `CI-tests <https://github.com/collective/icalendar/actions?query=branch%3Amaster>`__ are running on it.

    .. code-block:: bash

        git push
5. Create a tag for the release and see if the `CI-tests <https://github.com/collective/icalendar/actions>`__ are running.

    .. code-block:: bash

        git tag v5.0.0a2
        git push origin v5.0.0a2
6. TODO: how to release new version to PyPI.





