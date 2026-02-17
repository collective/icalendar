=======
Install
=======

This chapter describes how to install icalendar as a Python package for use in your projects.


Distribution Packages
---------------------

The `icalendar` package is also published in many Linux distributions.  
The following badge shows where it is available and wh  ich versions are packaged:

.. image:: https://camo.githubusercontent.com/622712ceb79dff491587f86e407468b88fcadeb003329d146478925c73e722ff/68747470733a2f2f7265706f6c6f67792e6f72672f62616467652f766572746963616c2d616c6c7265706f732f707974686f6e2533416963616c656e6461722e7376673f636f6c756d6e733d34
   :target: https://repology.org/project/python%3Aicalendar/versions
   :alt: Packaging status across distributions

Repology is a service that tracks the availability and versions of packages across many Linux distributions.
Clicking the badge above will take you to the Repology page where you can inspect distribution support.


Python package with pip
-----------------------

The following command will install the icalendar package with pip.

.. code-block:: shell

    pip install icalendar

If installation is successful, you will be able to import the iCalendar package from a Python interpreter as shown. 

.. code-block:: pycon

    >>> import icalendar


Debian or Ubuntu
----------------

You can install the `python-icalendar package <https://tracker.debian.org/pkg/python-icalendar>`_ for Debian or its derivatives.

.. code-block:: shell

    sudo apt-get install python3-icalendar


Arch Linux
-----------

On Arch Linux and derivatives, the package is available in the community repository:

.. code-block:: shell

    sudo pacman -S python-icalendar


Fedora
------

You can install the `python3-icalendar package <https://packages.fedoraproject.org/pkgs/python-icalendar/python3-icalendar/>`_ for Fedora or its derivatives.

.. code-block:: shell

    sudo dnf install python3-icalendar
