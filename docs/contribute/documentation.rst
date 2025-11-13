=============
Documentation
=============

This chapter describes how to contribute to icalendar's documentation, including narrative documentation and docstrings in Python code which get rendered into the :doc:`API reference documentation <../reference/api/icalendar>`.

.. button-link:: https://github.com/collective/icalendar/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22doc%22
    :color: success
    :shadow:

    Find open Documentation isues


.. _documentation-prerequisites:

Documentation prerequisites
---------------------------

Documentation builds require that you install GNU Make and uv.


Make
````

``make`` is used to provide an interface to developers to perform repetitive tasks with a single command.

``make`` comes installed on most Linux distributions.
On macOS, you must first [install Xcode](https://developer.apple.com/xcode/resources/), then install its command line tools.
On Windows, it is strongly recommended to [Install Linux on Windows with WSL](https://learn.microsoft.com/en-us/windows/wsl/install), which will include ``make``.

Finally, it is a good idea to update your system's version of ``make``, because some distributions, especially macOS, have an outdated version.
Use your favorite search engine or trusted online resource for how to update ``make``.


uv
``

`uv <https://docs.astral.sh/uv/>`_ is used for installing Python, creating a Python virtual environment, and managing dependencies for documentation.

Install uv.
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


Documentation builds
--------------------

All build and check commands use the file :file:`Makefile` at the root of the repository.

To see descriptions of the builds, use the following command.

.. code-block:: shell

    make help

Else you can open the :file:`Makefile` file to see other build formats.

The following sections describe the most frequently used ``make`` commands.

All ``make`` commands that build documentation will

-   create a Python virtual environment, and
-   install requirements.


``html``
````````

To build the documentation as HTML, run the following command.

.. code-block:: shell

    make html

You can now open the output from ``docs/_build/html/index.html``.


``livehtml``
````````````

``livehtml`` rebuilds documentation as you edit its files, with live reload in the browser.

.. code-block:: shell

    make livehtml

The console will give you the URL to open in a web browser.

.. code-block:: console

    [sphinx-autobuild] Serving on http://127.0.0.1:8050


``linkcheckbroken``
```````````````````

``linkcheckbroken`` checks all links, returning a list of only broken links.

.. code-block:: shell

    make linkcheckbroken

Open `docs/_build/linkcheck/output.txt` for the entire list of links that were checked and their result.


``vale``
````````

``vale`` checks for American English spelling, grammar, and syntax, and follows the Microsoft Writing Style Guide.
See {ref}`authors-english-label` for configuration.

.. code-block:: shell

    make vale

Observe the output and adjust Vale's configuration, as described in the next section.


Advanced Vale usage
+++++++++++++++++++

You can pass options to Vale in the ``VALEOPTS`` and ``VALEFILES`` environment variables.
In the following example, you can run Vale to display warnings or errors only, not suggestions, in the console on a single file.

.. code-block:: shell

    make vale VALEOPTS="--minAlertLevel='warning'" VALEFILES="docs/index.md"

The command ``make vale`` automatically installs Vale into your Python virtual environment—which is also created via any documentation ``Makefile`` commands—when you invoke it for the first time.

Vale has `integrations <https://vale.sh/docs/>`_ with various IDEs.
Integration might require installing Vale using operating system's package manager.

-   `JetBrains <https://plugins.jetbrains.com/plugin/19613-vale-cli/docs>`_
-   `Vim <https://github.com/dense-analysis/ale>`_
-   `VS Code <https://github.com/chrischinchilla/vale-vscode>`_

icalendar configures Vale in three places:

-   :file:`.vale.ini` is Vale's configuration file.
    This file allows overriding rules or changing their severity.
    It's configured to use the `Microsoft Writing Style Guide <https://learn.microsoft.com/en-us/style-guide/welcome/>`_ for its ease of use—especially for non-native English readers and writers—and attention to non-technical audiences.
-   :file:`Makefile` passes options to the ``vale`` command, such as the files Vale checks.
-   icalendar documentation uses a custom spelling dictionary, with accepted and rejected spellings in :file:`docs/styles/config/vocabularies/icalendar/`.
    Authors should add new words and proper names using correct casing to :file:`docs/styles/config/vocabularies/icalendar/accept.txt`, sorted alphabetically and case-insensitive.

    If Vale does not reject a spelling that should be rejected, then you can add it to {file}`docs/styles/config/vocabularies/icalendar/reject.txt`.
-   You can add additional spellings to accept or reject in their respective files inside the {file}`docs/styles/config/vocabularies/Base/` folder.

Because it's difficult to automate good American English grammar and syntax, it's not strictly enforced.

You can add spellings to Vale's configuration, and submit a pull request.
This is an easy way to become a contributor to icalendar.


``clean``
`````````

``clean`` removes all builds and cached files of the documentation.
Use this command before a build to troubleshoot issues with edits not showing up and to ensure that cached files do not hide errors in the documentation.

.. code-block:: shell

    make clean


``clean-python``
````````````````

``clean-python`` cleans the documentation build directory and Python virtual environment.
Use this command when packages that you have installed in your virtual environment yield unexpected results.

.. code-block:: shell

    make clean-python


``apidoc``
``````````

``apidoc`` generates source documentation files from which Sphinx will render the API documentation.

.. code-block:: shell

    make apidoc

When editing icalendar's Python source code, use `Google Python Style Guide <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_ for the docstring format.
The following is an example that will render properly.

.. code-block:: python

    def fetch_smalltable_rows(
        table_handle: smalltable.Table,
        keys: Sequence[bytes | str],
        require_all_keys: bool = False,
    ) -> Mapping[bytes, tuple[str, ...]]:
    """A one-line summary of the module or program, terminated by a period.

    Leave one blank line.  The rest of this docstring should contain an
    overall description of the module or program.  Optionally, it may also
    contain a brief description of exported classes and functions and/or usage
    examples.

    Args:
        table_handle:
            An open ``smalltable.Table`` instance.
        keys:
            A sequence of strings representing the key of each table row to
            fetch.  String keys will be UTF-8 encoded.
        require_all_keys:
            If True only rows with values set for all keys will be returned.

    Returns:
        A dict mapping keys to the corresponding table row data
        fetched. Each row is represented as a tuple of strings. For
        example:

        .. code-block:: python

            {b'Serak': ('Rigel VII', 'Preparer'),
            b'Zim': ('Irk', 'Invader'),
            b'Lrrr': ('Omicron Persei 8', 'Emperor')}

        Returned keys are always bytes.  If a key from the keys argument is
        missing from the dictionary, then that row was not found in the
        table (and require_all_keys must have been False).

    Raises:
        IOError:
            An error occurred accessing the smalltable.

    Example:
        The following is an example of using ``fetch_smalltable_rows``.

        .. code-block: pycon

            >>> fetch_smalltable_rows(my_table_handle, (b'Serak', b'Zim', b'Lrrr'))
            {b'Serak': ('Rigel VII', 'Preparer'),
            b'Zim': ('Irk', 'Invader'),
            b'Lrrr': ('Omicron Persei 8', 'Emperor')}

    """

.. seealso::

    `sphinx-apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_
