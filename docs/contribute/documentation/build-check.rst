.. _build-check:

===============
Build and check
===============

This chapter describes how to build and check the quality of documentation.


.. _documentation-prerequisites:

Prerequisites
-------------

You'll need to first install prerequisites on, and clone the icalendar repository to, your local computer.

Documentation builds and checks require that you install :program:`GNU Make` and :program:`uv`.


:program:`Make`
'''''''''''''''

:program:`Make` is used to provide an interface to developers to perform repetitive tasks with a single command.

:program:`Make` comes installed on most Linux distributions.
On macOS, you must first `install Xcode <https://developer.apple.com/xcode/resources/>`_, then install its command line tools.
On Windows, it is strongly recommended to `Install Linux on Windows with WSL <https://learn.microsoft.com/en-us/windows/wsl/install>`_, which will include :program:`Make`.

Finally, it is a good idea to update your system's version of :program:`Make`, because some distributions, especially macOS, have an outdated version.
Use your favorite search engine or trusted online resource for how to update :program:`Make`.


uv
''

`uv <https://docs.astral.sh/uv/>`_ is used for installing Python, creating a Python virtual environment, and managing dependencies for documentation.

Install :program:`uv`.
Read the console output for further instructions, and follow them, if needed.

.. tab-set::

    .. tab-item:: macOS, Linux, and Windows with WSL

        .. code-block:: shell

            curl -LsSf https://astral.sh/uv/install.sh | sh

    .. tab-item:: Windows

        .. code-block:: shell

            powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

.. seealso::

    `Other uv installation methods <https://docs.astral.sh/uv/getting-started/installation/>`_


Clone repository
''''''''''''''''

To clone the icalendar repository, open a terminal session, and use the following command.

.. code-block:: shell

    git clone https://github.com/collective/icalendar.git


Change your working directory into the cloned project.

.. code-block:: shell

    cd documentation


.. _file-locations:

File locations
--------------

Narrative documentation files are located in the `docs <https://github.com/collective/icalendar/tree/main/docs>`_ directory.

:doc:`API reference documentation files </reference/api/icalendar>` are located in the `src <https://github.com/collective/icalendar/tree/main/docs>`_ directory.


.. _make-commands:

:program:`Make` commands
------------------------

With all :ref:`prerequisites <documentation-prerequisites>` installed, you can make various documentation builds, perform quality checks, and clean your environment.
All :program:`Make` commands use the file :file:`Makefile` at the root of the repository.

The :program:`Make` commands may invoke :program:`Sphinx`, :program:`uv`, :program:`Vale`, shell commands, and other programs.


Help
''''

To get help and see descriptions of the ``make`` commands, use the following command.

.. code-block:: shell

    make help

Alternatively, the :file:`Makefile` file at the root of the repository contains all available commands.

All commands except the "clean" commands will create a Python virtual environment, and install requirements.


Live HTML preview
'''''''''''''''''

``livehtml`` rebuilds documentation as you edit its files, providing a preview with live reload in the browser.
This is the most useful command when editing documentation.

.. code-block:: shell

    make livehtml

The console will give you the URL to open in a web browser.

.. code-block:: console

    [sphinx-autobuild] Serving on http://127.0.0.1:8050


HTML
''''

To build the documentation as HTML without live reload, run the following command.

.. code-block:: shell

    make html

You can now open the output file :file:`_build/html/index.html` in a web browser to view static content.

This build must be successful in the :ref:`continuous-integration-checks` for your pull request to be merged.


Check links
'''''''''''

``linkcheckbroken`` checks all links, returning a list of only broken links.

.. code-block:: shell

    make linkcheckbroken

Open :file:`_build/linkcheck/output.txt` for the entire list of links that were checked and their result.

This build must be successful in the :ref:`continuous-integration-checks` for your pull request to be merged.


.. _make-vale:

Spelling, grammar, and style
''''''''''''''''''''''''''''

``vale`` checks American English spelling, grammar, and syntax, and follows the Microsoft Writing Style Guide.

.. code-block:: shell

    make vale

Observe the output and adjust Vale's configuration, as described in the next section.


.. _vale-options:

Vale options
````````````

Pass options to Vale in the ``VALEOPTS`` and ``VALEFILES`` environment variables.
In the following example, run Vale to display warnings or errors only, not suggestions, in the console on a single file.

.. code-block:: shell

    make vale VALEOPTS="--minAlertLevel='warning'" VALEFILES="docs/index.rst"

The command ``make vale`` automatically installs Vale into your Python virtual environment when you invoke it the first time.

This build must be successful in the :ref:`continuous-integration-checks` for your pull request to be merged.


.. _vale-integration:

Vale integration
````````````````

Vale has `integrations <https://vale.sh/docs/>`_ with various IDEs.
Integration might require installing Vale using your operating system's package manager.

-   `JetBrains <https://plugins.jetbrains.com/plugin/19613-vale-cli/docs>`_
-   `Vim <https://github.com/dense-analysis/ale>`_
-   `VS Code <https://github.com/chrischinchilla/vale-vscode>`_


.. _vale-configuration:

Vale configuration
``````````````````

icalendar configures Vale in the following places:

-   :file:`.vale.ini` is Vale's configuration file.
    This file allows overriding rules or changing their severity.
    It's configured to use the `Microsoft Writing Style Guide <https://learn.microsoft.com/en-us/style-guide/welcome/>`_ for its ease of use—especially for non-native English readers and writers—and attention to non-technical audiences.
-   :file:`Makefile` passes options to the ``vale`` command, such as the files Vale checks.
-   icalendar documentation uses a custom spelling dictionary, with accepted and rejected spellings in :file:`docs/styles/config/vocabularies/icalendar/`.
    Authors should add new words and proper names using correct casing to :file:`docs/styles/config/vocabularies/icalendar/accept.txt`, sorted alphabetically and case-insensitive.

    If Vale does not reject a spelling that should be rejected, then you can add it to :file:`docs/styles/config/vocabularies/icalendar/reject.txt`.

    All entries in both files support regular expressions.
    Use https://regex101.com/ with the :guilabel:`Golang` option selected to test regular expressions.

    .. seealso::

        Vale's `regex guide <https://vale.sh/docs/guides/regex>`_

-   Add generic spellings to accept or reject in their respective files inside the :file:`docs/styles/config/vocabularies/Base/` folder.

Because it's difficult to automate good American English grammar and syntax, it's not strictly enforced.

You can add spellings to Vale's configuration, and submit a pull request.
This is an easy way to become a contributor to icalendar.


Build API source files
''''''''''''''''''''''

``apidoc`` generates source documentation files from which Sphinx will render the API documentation.
This command should be used when either:

- adding a new module, that is, a Python file in the :file:`src/icalendar` directory
- changing the options of source reStructuredText files to build API documentation

.. code-block:: shell

    make apidoc

.. seealso::

    :doc:`sphinx:man/sphinx-apidoc`

Purge builds
''''''''''''

``clean`` removes all builds and cached files of the documentation.
Use this command before a build to troubleshoot issues with edits not showing up and to ensure that cached files do not hide errors in the documentation.
This is especially useful when adding a new page to the documentation and it doesn't appear in the navigation.
Sphinx only rebuilds changed files.

.. code-block:: shell

    make clean


Purge environment
'''''''''''''''''

``clean-python`` cleans the documentation build directory and Python virtual environment.
Use this command when packages that you have installed in your virtual environment yield unexpected results.

.. code-block:: shell

    make clean-python


Add features
------------

To add features to documentation through Sphinx extensions and other programs, you might need to perform the following tasks.


Add a package
'''''''''''''

To add a package for documentation, such as a Sphinx extension or other third application, use :program:`uv`.

.. code-block:: shell

    uv add --group docs new-requirement

This will add ``new-requirement`` to the list of documentation requirements in the ``docs`` group in the :file:`pyproject.toml` file.


.. _configure-a-package:

Configure a package
'''''''''''''''''''

Most packages require configuration in Sphinx and in the :file:`Makefile` file.
Follow the specific directions of the package.

For Sphinx, you would typically edit the file :file:`docs/conf.py`, and add both the package's Python name to the ``extensions`` list and its configuration options as a new section.
For the latter, use a comment with a visual separator, such as that for configuring the Napolean extension.

.. code-block:: python

    # -- Napolean configuration ----------------------------------
    napoleon_use_param = True
    napoleon_google_docstring = True
    napoleon_attr_annotations = True

If your feature adds a shell command, add helpful options to the :file:`Makefile` file.


Document a package
''''''''''''''''''

    "If it ain't documented, it's broken."

After adding and configuring a package, it's important to inform other people what the feature does and how to use it.


Pull request previews
---------------------

On every pull request, Read the Docs generates a pull request preview of the documentation.
It will append a link to the preview in the description of the pull request that the author creates.

`View all builds of documentation on Read the Docs <https://app.readthedocs.org/projects/icalendar/builds/>`_.

This feature is configured in the files :file:`.readthedocs.yml` and :file:`.github/workflows/rtd-pr-preview.yml`.


.. _continuous-integration-checks:

Continuous integration checks
-----------------------------

On every pull request, continuous integration checks attempt to build the documentation, run Vale checks, and check for broken links.
If any of these checks fail, then the pull request cannot be merged.
You must resolve the build failures, preferably locally, before the pull request can be merged.

This feature is configured in the file :file:`.github/workflows/documentation.yml`.
