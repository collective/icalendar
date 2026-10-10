
.. _safe-xml-parsing:

================
Safe XML parsing
================

This chapter explains the design decisions made for safe XML parsing in icalendar.

:rfc:`6321` specifies how to represent calendars as XML.

In summary, Python's built-in XML parser is reasonably safe to parse XML for xCal.

Sources
=======

The following sources have been taken into consideration:

#. `Python 3.12 XML package <https://docs.python.org/3.12/library/xml.html#xml-vulnerabilities>`_ still mentions `defusedxml <https://pypi.org/project/defusedxml/>`_.
#. `Python 3.13 XML package <https://docs.python.org/3.13/library/xml.html#xml-vulnerabilities>`_ does not mention `defusedxml`_.
#. `Amended documentation recommendation <https://github.com/python/cpython/pull/135294>`_

       "Python 3.11-3.15 include expat 2.7.1 which is not vulnerable."

#. `Discussion on defusedxml <https://discuss.python.org/t/status-of-defusedxml-and-recommendation-in-docs/34762/21>`_
#. `RUFF checker flagging built-in XML parser <https://github.com/astral-sh/ruff/discussions/3697>`_
#. `defusedxml analysis <https://github.com/tiran/defusedxml/blob/c7445887f5e1bcea470a16f61369d29870cfcfe1/README.md#python-xml-libraries>`_
#. `xinclude support <https://runebook.dev/en/docs/python/library/xml.etree.elementtree/xinclude-support>`_

People who use icalendar may parse unverified, external XML.
Therefore, the XML parser should be safe.
If it isn't safe, then icalendar can refuse to parse content, and raise a exception that refers to a solution.

Conclusion
==========

Python 3.10 ships with expat >= 2.4.1.
According to `defusedxml analysis`_, XML parsing is safe in Python 3.10.

Python 3.11 or later ships expat >= 2.7.1.
According to `Amended documentation recommendation`_, in these Python versions, XML parsing is safe.

icalendar's :file:`pyproject.toml` file requires a Python version that is safe for XML parsing.
Therefore, icalendar is safe to use its configured built-in XML parsing.

Developers can `open an issue <https://github.com/collective/icalendar/issues/new?template=empty-issue.md>`_ to use a different XML parser.
The parser is configurable through the setting :func:`icalendar.config.parse_xml`.

.. seealso::

    :mod:`icalendar.tests.rfc_6321_xcal.test_xml_parser`
