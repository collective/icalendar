=====================
BASE64 value encoding
=====================

BASE64 represents the bytes of a property value with ASCII characters.
The property still has a value type, such as ``TEXT``, ``DATE``, or ``BINARY``.

For a non-binary value with ``ENCODING=BASE64``, icalendar first decodes the BASE64 data.
It then reads the bytes as UTF-8 and parses the text according to the property's value type.
For example, a ``SUMMARY`` becomes text, while a ``DTSTART`` with ``VALUE=DATE`` becomes a date.
The parser removes ``ENCODING`` from these values and keeps their other parameters.

This distinction also matters when converting to jCal or xCal.
Both formats require decoded non-binary values without the ``ENCODING`` parameter, as specified in :rfc:`7265#section-3.1` and :rfc:`6321#section-3.1`.
For binary values, icalendar keeps the bytes without UTF-8 decoding.
It uses BASE64 when it writes these values to iCalendar, jCal, or xCal.

See :ref:`read-base64-values` for a parsing example.
