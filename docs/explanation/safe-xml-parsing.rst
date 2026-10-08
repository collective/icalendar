
.. _safe-xml-parsing:

================
Safe XML parsing
================

:rfc:`6321` specifies how to represent calendars as XML.

Summary: Python's built-in XML parser is considered safe enough to parse XML for xCal.

Sources
=======

The following sources have been taken into consideration:

#. `Python 3.12 XML package <https://docs.python.org/3.12/library/xml.html#xml-vulnerabilities>`_
#. `Python 3.13 XML package <https://docs.python.org/3.13/library/xml.html#xml-vulnerabilities>`_
#. `Amended documentation recommendation <https://github.com/python/cpython/pull/135294>`_

       "Python 3.11-3.15 include expat 2.7.1 which is not vulnerable."

#. `Discussion on defusedxml <https://discuss.python.org/t/status-of-defusedxml-and-recommendation-in-docs/34762/21>`_
#. `RUFF checker flagging built-in XML parser <https://github.com/astral-sh/ruff/discussions/3697>`_
#. `defusedxml analysis <https://github.com/tiran/defusedxml/blob/c7445887f5e1bcea470a16f61369d29870cfcfe1/README.md#python-xml-libraries>`_
#. `xinclude support <https://runebook.dev/en/docs/python/library/xml.etree.elementtree/xinclude-support>`_

We can expect people who use icalendar to parse unverified, external XML.
Therefore, we should make sure that the XML parser is safe.
If it isn't safe, we can just refuse to parse content and
refer to a solution.

Conclusion
==========

We must ensure Python is >= 3.11 or XML loading may be vulnerable.
:file:`pyproject.toml` currently requires Python >= 3.8; once the minimum is
raised to 3.11, there is nothing further to do.

People can open an issue if they like to use a different XML parser.


.. seealso::

    :func:`icalendar.config.parse_xml`
    :mod:`icalendar.tests.rfc_6321_xcal.test_xml_parser`
