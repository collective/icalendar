===========
Development
===========

This chapter describes how to set up icalendar for development and to contribute changes.



To start contributing changes to icalendar, you can clone the project to your file system using Git.
You can `fork <https://github.com/collective/icalendar/fork>`_
the project first and clone your fork, too.

.. code-block:: shell

    git clone https://github.com/collective/icalendar.git
    cd icalendar


Install Python
--------------

You will need a version of Python installed on your system to run the tests and execute the code.
The latest version of Python 3 should work and will be enough to get you started.
If you like to run the tests across multiple Python versions, then the following setup process should work the same.


Install tox
-----------

First, install `tox <https://pypi.org/project/tox/>`_.

.. code-block:: shell

    pip install tox

From now on, tox will manage Python versions and test commands for you.


Run tests
---------

tox manages all test environments in all Python versions.

To run all tests in all environments, run the command ``tox``.

.. code-block:: shell

    tox

You might not have all Python versions installed or you may want to run a specific one.
The following command show how to run tox with Python 3.12:

.. code-block:: shell

    tox -e py312

.. seealso::

    tox's `documentation <https://tox.wiki/en/stable/user_guide.html#cli>`_.


Code style
----------

We strive towards a common code style.
You can run the following command to auto-format the code.

.. code-block:: shell

    tox -e ruff


Activate a tox environment
--------------------------

If you'd like to activate a specific tox virtual environment, use the following command, replacing the Python version accordingly.

.. code-block:: shell

    source .tox/py312/bin/activate


Install icalendar manually
--------------------------

The best way to test the package is to use tox as described above.

However, if you can't install tox, or you'd like to use your local copy of icalendar in another Python environment, this section describes how to use your installed version of Python and pip.

.. code-block:: shell

    cd src/icalendar
    python -m pip install -e .

The above commands install icalendar and its dependencies in your Python environment so that you can access local changes.
If tox fails to install icalendar during its first run, you can activate the environment in the :file:`.tox` folder and manually set up icalendar as shown above.

To verify installation, launch a Python interpreter, and issue the following statements.

.. code-block:: pycon

    Python 3.12.0 (main, Mar  1 2024, 09:09:21) [GCC 13.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import icalendar
    >>> icalendar.Calendar()
    VCALENDAR({})


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
Carefully read the console output for further instructions, and follow them, if needed.

.. tab-set::

    .. tab-item:: macOS, Linux, and Windows with WSL

        .. code-block:: shell

            curl -LsSf https://astral.sh/uv/install.sh | sh

    .. tab-item:: Windows

        .. code-block:: shell

            powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

.. seealso::

    [Other {term}`uv` installation methods](https://docs.astral.sh/uv/getting-started/installation/)


Documentation builds
--------------------

All build and check commands use the file :file:`Makefile` at the root of the repository.

To see descriptions of the builds, use the following command.

.. code-block:: shell

    make help

Else you can open the :file:`Makefile` file to see other build formats.

The following sections describe the most frequently used ``make`` commands.

All ``make`` commands that build documentation will

-   create a Python virtual environment,
-   install requirements,
-   initialize or update the `volto`, `plone.restapi`, and `plone.api` submodules, and
-   finally create symlinks to the source files.


html
````

To build the documentation as HTML, run the following command.

.. code-block:: shell

    make html

You can now open the output from ``docs/_build/html/index.html``.


livehtml
````````

``livehtml`` rebuilds documentation as you edit its files, with live reload in the browser.

.. code-block:: shell

    make livehtml

The console will give you the URL to open in a web browser.

.. code-block:: console

    [sphinx-autobuild] Serving on http://127.0.0.1:8050


linkcheckbroken
```````````````

``linkcheckbroken`` checks all links, returning a list of only broken links.

.. code-block:: shell

    make linkcheckbroken

Open `docs/_build/linkcheck/output.txt` for the entire list of links that were checked and their result.


.. For future implementation
.. ### `vale`

.. `vale` checks for American English spelling, grammar, and syntax, and follows the Microsoft Writing Style Guide.
.. See {ref}`authors-english-label` for configuration.

.. .. code-block:: shell

.. make vale

.. See the output on the console for suggestions.


clean
`````

``clean`` removes all builds and cached files of the documentation.
Use this command before a build to troubleshoot issues with edits not showing up and to ensure that cached files do not hide errors in the documentation.

.. code-block:: shell

    make clean


clean-python
````````````

``clean-python`` cleans the documentation build directory and Python virtual environment.
Use this command when packages that you have installed in your virtual environment yield unexpected results.

.. code-block:: shell

    make clean-python


apidoc
``````

``apidoc`` generates source documentation files from which Sphinx will render the API documentation.

.. code-block:: shell

    make apidoc

.. seealso::

    `sphinx-apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html>`_
