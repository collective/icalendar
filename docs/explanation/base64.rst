=====================
BASE64 value encoding
=====================

Base64 represents bytes with ASCII characters.
iCalendar uses Base64 for binary data and can also use it for non-binary values.
The icalendar package uses Python's :mod:`base64` module to encode and decode these values.

The ``ENCODING`` parameter specifies the encoding of a property value.
Its values are ``BASE64`` and ``8BIT``.
The default is ``8BIT`` when the parameter is absent.

A property's value type is separate from its encoding.
The ``VALUE`` parameter can specify a type, such as ``TEXT``, ``DATE``, or ``BINARY``.
When ``VALUE`` is absent, the property's default type applies.
The ``VALUE=BINARY`` parameter requires ``ENCODING=BASE64``, as specified in :rfc:`5545#section-3.2.7`.

This property contains an inline PNG attachment.

..  code-block:: text

    ATTACH;FMTTYPE=image/png;ENCODING=BASE64;VALUE=BINARY:iVBORw0KGgoAAAANSUhEU
     gAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAEl
     FTkSuQmCC

Each continuation line starts with one space.

For a non-binary value with ``ENCODING=BASE64``, icalendar first decodes the BASE64 data.
It then reads the bytes as UTF-8 and parses the text according to the property's value type.
For example, a ``SUMMARY`` becomes text, while a ``DTSTART`` with ``VALUE=DATE`` becomes a date.
The parser removes ``ENCODING`` from these values and keeps the other parameters.

This distinction also matters when you convert iCalendar data to jCal or xCal.
Both jCal and xCal require decoded non-binary values without the ``ENCODING`` parameter.
See :rfc:`7265#section-3.1` and :rfc:`6321#section-3.1`.
For binary values, :class:`~icalendar.prop.vBinary` keeps the bytes without UTF-8 decoding.
It uses BASE64 when it writes these values to iCalendar, jCal, or xCal.

See :ref:`read-base64-values` for a parsing example.
