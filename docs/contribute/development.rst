===========
Development
===========

This chapter describes how to set up icalendar for development and to contribute changes.


.. _development-prerequisites:

.. include:: ../_include/prerequisites.inc

.. _development-configure-git:

.. include:: ../_include/configure-git.inc
.. include:: ../_include/configure-git-card-dev.inc
.. include:: ../_include/configure-git-steps.inc


Install icalendar for development
---------------------------------

To install icalendar for development—including all of its dependencies for tests, documentation, and formatting code, as well as a Python virtual environment—run the following command.

.. code-block:: shell

    make dev


.. _development-make-commands:

:program:`Make` commands
------------------------

With all :ref:`prerequisites <development-prerequisites>` installed, you can run tests, reformat code, make various documentation builds, perform quality checks, and clean your environment.
All :program:`Make` commands use the file :file:`Makefile` at the root of the repository.

The :program:`Make` commands may invoke :program:`uv`, :program:`tox`, :program:`Sphinx`, :program:`Vale`, shell commands, and other programs.


pre-commit
----------

`pre-commit <https://pre-commit.com/>`_ is automatically installed as one of the development requirements when running the following command.

.. code-block:: shell

    make dev

That command installs a supported Python, creates a Python virtual environment, and installs package and development requirements.

When you commit code to icalendar with ``git commit``, pre-commit runs the following code quality checks and reformats code automatically for you.

`debug-statements <https://github.com/pre-commit/pre-commit-hooks#debug-statements>`_
    Checks for debugger imports and Python 3.7+ ``breakpoint()`` calls in Python source code.
`ruff check --fix <https://docs.astral.sh/ruff/linter/#ruff-check>`_
    Runs the Ruff linter on Python files and fixes issues according to the configuration in :file:`pyproject.toml`.
`ruff format <https://docs.astral.sh/ruff/formatter/#ruff-format>`_
    Runs the Ruff formatter on Python files and fixes issues according to the configuration in :file:`pyproject.toml`.

The configuration file for pre-commit, :file:`.pre-commit-config.yaml`, is located at the root of the repository.

Contributors to icalendar are encouraged to use pre-commit.
Any issues that would be caught by pre-commit shall be caught by GitHub workflows when you push commits to a pull request for icalendar.
This could delay merging of your pull request.

However, you may opt out of using pre-commit.
You can use the ``--no-validate`` flag for the ``git commit`` command.

.. code-block:: shell

    git commit -m "My commit message" --no-validate

Alternatively, configure your editor to use ``--no-validate`` for all commits.
The screenshot below shows how to configure PyCharm to disable pre-commit by searching for "git commit hooks" in its settings.

.. card::

    .. image:: ../_static/contributing/development-disable-pre-commit.png
        :alt: Disable pre-commit in PyCharm settings
        :target: ../_static/contributing/development-disable-pre-commit.png

    +++
    *Disable pre-commit in PyCharm settings*


Run tests
---------

Through :program:`uv`, :program:`tox` manages all test environments across all Python versions.

To run all tests in all environments, run the following command.

..  code-block:: shell

    make test

The following command shows how to run tests in the Python 3.14.

..  code-block:: shell

    make test TOX_ENV=py314

.. seealso::

    tox's `CLI interface documentation <https://tox.wiki/en/stable/reference/cli.html>`_.


Format code
-----------

icalendar requires code formatting.
You can run the following command to automatically format the code.

..  code-block:: shell

    make format


Code conventions
----------------

icalendar has adopted code conventions to help make its code more legible and understandable.


Internal use only
'''''''''''''''''

There are no truly private methods in Python.
However, icalendar follows the :pep:`8` Python style guide regarding the use of a single leading underscore character ``_`` to the object as "internal use only."

"Internal use only" methods and variables are not part of icalendar's public API, and developers should not use them in their code.
These are implementation details that may change without notice.

In addition, "internal use only" objects are not displayed in the documentation.
Their docstrings, of course, remain in the Python source code.


Type hints
''''''''''

Type hints in Python help developers catch errors early, improve code documentation, and enhance the functionality of IDEs and linters.
icalendar uses type hints, and supports rendering them in its :doc:`reference API documentation </reference/api/icalendar>`.

icalendar was originally written before the existence of type hints in Python.
As such, there are many Python objects in the code base that lack type hints.
The icalendar team welcomes contributions to add type hints.

When the type hints in the standard library are not sufficient, you can use subtyping through :doc:`protocols <typing:spec/protocol>`.
The following example demonstrates subtyping through the usage of a protocol and a method using a literal :ref:`ellipsis <bltin-ellipsis-object>` ``...`` to indicate that the method signature exists, but the implementation details aren't necessary.

.. code-block:: python

    class HasToIcal(Protocol):
        """Protocol for objects with a to_ical method."""

        def to_ical(self) -> bytes:
            """Convert to iCalendar format."""
            ...

.. seealso::

    - GitHub issue :issue:`Add type hints <938>`
    - :ref:`markup-and-formatting`
    - :doc:`typing:index`
    - Python standard library :mod:`typing`
    - :ref:`annotating-callables`


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
