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

icalendar strives towards a common code style.
You can run the following command to automatically format the code.

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
