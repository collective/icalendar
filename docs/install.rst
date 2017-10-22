Installing iCalendar
====================

To install the icalendar package, use::

  pip install icalendar

If installation is successful, you will be able to import the iCalendar
package, like this::

  >>> import icalendar


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
