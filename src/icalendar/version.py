"""Version information on icalendar.

This module is the stable interface for the generated _version.py file.

Version as a string:

.. code-block:: pycon

    >>> from icalendar import version

Version as a tuple:

.. code-block:: pycon

    >>> from icalendar import version_tuple

"""

try:
    from ._version import __version__, __version_tuple__, version, version_tuple
except ModuleNotFoundError:
    __version__ = version = "0.0.0dev0"
    __version_tuple__ = version_tuple = (0, 0, 0, "dev0")

__all__ = [
    "__version__",
    "__version_tuple__",
    "version",
    "version_tuple",
]
