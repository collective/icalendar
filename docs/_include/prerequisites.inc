Prerequisites
-------------

You'll need to first install prerequisites on, and clone the icalendar repository to, your local computer.

Tests, code formatting, and documentation builds and checks require that you install :program:`GNU Make`, :program:`uv`, and :program:`Git`.

.. note::

    :program:`uv` handles the installation of Python and all dependencies for icalendar.


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

    .. tab-item:: Other

        `Other uv installation methods <https://docs.astral.sh/uv/getting-started/installation/>`_

Git
'''

Install `Git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_ for your operating system.

