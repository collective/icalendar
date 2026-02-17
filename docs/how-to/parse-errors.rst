=====================
Handle parsing errors
=====================

iCalendar files from a source might contain invalid property values.
By default, event components use error-tolerant parsing, allowing you to work with partially valid calendar data.

.. note::

    To avoid repetition, the code examples in this chapter use the following imports.

    .. code-block:: pycon

        >>> from icalendar import Calendar, BrokenCalendarProperty
        >>> from icalendar.prop import vBroken


Check for parsing errors
------------------------

When a component is parsed, any properties with invalid values are recorded in the ``errors`` attribute.
This attribute is a list of tuples containing the property name and error information.

.. code-block:: pycon

    >>> ical_str = b"""BEGIN:VCALENDAR
    ... VERSION:2.0
    ... PRODID:test
    ... BEGIN:VEVENT
    ... UID:test-123
    ... DTSTART:INVALID-DATE
    ... SUMMARY:Meeting
    ... END:VEVENT
    ... END:VCALENDAR"""
    >>> cal = Calendar.from_ical(ical_str)
    >>> event = cal.walk("VEVENT")[0]
    >>> event.errors
    [('DTSTART', "Expected datetime, date, or time. Got: 'INVALID-DATE'")]

Errors are populated immediately after parsing, without needing to access the problematic properties.


Access broken properties
------------------------

Properties that fail to parse are converted to :class:`~icalendar.prop.broken.vBroken` instances.
This preserves the raw value for inspection or round-trip serialization.

.. code-block:: pycon

    >>> dtstart = event["DTSTART"]
    >>> isinstance(dtstart, vBroken)
    True
    >>> str(dtstart)
    'INVALID-DATE'

The broken property includes metadata about the parsing failure.

.. code-block:: pycon

    >>> dtstart.property_name
    'DTSTART'
    >>> dtstart.expected_type
    'vDDDTypes'
    >>> isinstance(dtstart.parse_error, Exception)
    True


Work with partially valid data
------------------------------

One broken property does not prevent access to other valid properties in the same component.

.. code-block:: pycon

    >>> ical_str = b"""BEGIN:VCALENDAR
    ... VERSION:2.0
    ... PRODID:test
    ... BEGIN:VEVENT
    ... UID:test-123
    ... DTSTART:INVALID-DATE
    ... DTEND:20250102T120000Z
    ... SUMMARY:Meeting
    ... END:VEVENT
    ... END:VCALENDAR"""
    >>> cal = Calendar.from_ical(ical_str)
    >>> event = cal.walk("VEVENT")[0]
    >>> event["DTEND"].dt.year
    2025
    >>> str(event["SUMMARY"])
    'Meeting'


Round-trip serialization
------------------------

Broken properties preserve their raw values, so they serialize correctly with :meth:`~icalendar.Component.to_ical`.

.. code-block:: pycon

    >>> output = cal.to_ical()
    >>> b"DTSTART:INVALID-DATE" in output
    True


Handle errors programmatically
------------------------------

You can iterate over errors to log or handle them.

.. code-block:: pycon

    >>> for prop_name, error_msg in event.errors:
    ...     print(f"{prop_name}: {error_msg}")
    DTSTART: Expected datetime, date, or time. Got: 'INVALID-DATE'

To check if a specific property failed to parse, check if it is a :class:`~icalendar.prop.broken.vBroken`.

.. code-block:: pycon

    >>> if isinstance(event["DTSTART"], vBroken):
    ...     print("DTSTART failed to parse")
    DTSTART failed to parse


Catch broken property access
----------------------------

When you access a property descriptor like :attr:`event.DTSTART <icalendar.cal.event.Event.DTSTART>` on a broken property, a :class:`~icalendar.error.BrokenCalendarProperty` is raised with the original parse error chained as ``__cause__``.

.. code-block:: pycon

    >>> try:
    ...     event.DTSTART
    ... except BrokenCalendarProperty as e:
    ...     print(f"Broken: {e}")
    ...     print(f"Original error: {e.__cause__}")
    Broken: Cannot access 'dt' on broken property 'DTSTART' (expected 'vDDDTypes'): Expected datetime, date, or time. Got: 'INVALID-DATE'
    Original error: Expected datetime, date, or time. Got: 'INVALID-DATE'

:class:`~icalendar.error.BrokenCalendarProperty` is a subclass of :class:`~icalendar.error.InvalidCalendar`, so existing ``except InvalidCalendar`` handlers will still catch it.
