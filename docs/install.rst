Installing iCalendar
====================

To install the icalendar package, use::

  pip install icalendar

If installation is successful, you will be able to import the iCalendar
package, like this::

  >>> import icalendar

Development Setup
-----------------

To start contributing changes to icalendar,
you can clone the project to your file system
using Git.
You can `fork <https://github.com/collective/icalendar/fork>`_
the project first and clone your fork, too.

.. code-block:: bash

    git clone https://github.com/collective/icalendar.git
    cd icalendar

Installing Python
-----------------

You will need a version of Python installed to run the tests
and execute the code.
The latest version of Python 3 should work and will be enough
to get you started.
If you like to run the tests with different Python versions,
the following setup proecess should work the same.

Install Virtualenv
------------------

First, install ``virtualenv`` and create a virtual Python
environment.

.. code-block:: bash

    pip install virtualenv
    virtualenv -p python3 virtualenv-3

Now, you need to execute the following each time you
open a new command line to activate this specific environment.

.. code-block:: bash

    source virtualenv-3/bin/activate

If for some reason you cannot install ``vitualenv``, you can
go ahead with the following section using your
installed version of Python and ``pip``.

Install Dependencies
--------------------

You can install the local copy of ``icalendar`` with ``pip``.

.. code-block:: bash

    cd icalendar
    python -m pip install -e .

This installs the module and dependencies in your
Python environment so that you can access local changes.

Try it out:

.. code-block:: python

    Python 3.9.5 (default, Nov 23 2021, 15:27:38)
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import icalendar
    >>> icalendar.__version__
    '4.0.10.dev0'

Building the documentation locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To build the documentation follow these steps:

.. code-block:: bash

    $ git clone https://github.com/collective/icalendar.git
    $ cd icalendar
    $ virtualenv-2.7 .
    $ source bin/activate
    $ pip install -r requirements_docs.txt
    $ cd docs
    $ make html

You can now open the output from ``_build/html/index.html``. To build the
presentation-version use ``make presentation`` instead of ``make html``. You
can open the presentation at ``presentation/index.html``.
