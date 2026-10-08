icalendar.prop.binary module
============================

.. automodule:: icalendar.prop.binary
   :ignore-module-all:
   :members:
   :show-inheritance:
   :undoc-members:

For example, a binary property can expose its current bytes as a base64 data
URI while retaining its ``FMTTYPE`` parameter:

.. code-block:: pycon

   >>> from icalendar import vBinary
   >>> vBinary(b"hello", params={"FMTTYPE": "text/plain"}).uri
   'data:text/plain;base64,aGVsbG8='
