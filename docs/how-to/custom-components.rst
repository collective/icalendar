==================
Custom Components
==================

icalendar automatically handles X-components and IANA-components not in RFC 5545.

Overview
========

RFC 5545 defines two custom component types:

- **X-Components**: Vendor-specific (e.g., ``X-MYAPP-SETTINGS``)
- **IANA-Components**: IANA-registered but not in RFC 5545

The library preserves all custom components through dynamic component creation using :py:class:`~icalendar.cal.component_factory.ComponentFactory`. No configuration needed.

Parsing Custom Components
==========================

You can parse custom components using either :py:meth:`Component.from_ical() <icalendar.Component.from_ical>` or :py:meth:`Calendar.from_ical() <icalendar.Calendar.from_ical>`.

Using Component.from_ical()
----------------------------

Parse any component type, including custom ones:

.. code-block:: pycon

    >>> from icalendar import Component
    >>> ics_data = b"""BEGIN:X-MYCOMPONENT
    ... SUMMARY:Custom component example
    ... X-CUSTOM-PROP:Some value
    ... END:X-MYCOMPONENT
    ... """
    >>> component = Component.from_ical(ics_data)
    >>> component.name
    'X-MYCOMPONENT'
    >>> component['SUMMARY']
    'Custom component example'

Using Calendar.from_ical()
---------------------------

Parse a calendar containing custom components:

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> ics_data = b"""BEGIN:VCALENDAR
    ... VERSION:2.0
    ... PRODID:-//Example//EN
    ... BEGIN:X-CUSTOM
    ... UID:custom-1
    ... SUMMARY:A custom component
    ... END:X-CUSTOM
    ... END:VCALENDAR
    ... """
    >>> cal = Calendar.from_ical(ics_data)
    >>> custom = cal.subcomponents[0]
    >>> custom.name
    'X-CUSTOM'
    >>> custom['UID']
    'custom-1'

Accessing Custom Components
============================

Custom components work exactly like standard components:

.. code-block:: pycon

    >>> from icalendar import Component
    >>> # Parse custom component
    >>> comp = Component.from_ical(b"BEGIN:MYCOMP\\r\\nEND:MYCOMP\\r\\n")
    >>> comp.name
    'MYCOMP'
    >>>
    >>> # Add properties
    >>> comp.add('summary', 'Test Summary')
    >>> comp.add('x-custom-field', 'Custom Value')
    >>>
    >>> # Access properties
    >>> comp['SUMMARY']
    'Test Summary'
    >>> comp.get('X-CUSTOM-FIELD')
    'Custom Value'
    >>>
    >>> # Add subcomponents
    >>> from icalendar import Event
    >>> event = Event()
    >>> event.add('uid', '123')
    >>> comp.add_component(event)
    >>> len(comp.subcomponents)
    1

Round-Trip Preservation
=======================

Custom components are fully preserved during round-trip parsing:

.. code-block:: pycon

    >>> from icalendar import Calendar
    >>> original = b"""BEGIN:VCALENDAR
    ... VERSION:2.0
    ... PRODID:-//Test//EN
    ... BEGIN:X-VENDOR-COMPONENT
    ... X-VENDOR-PROP:proprietary
    ... UID:vendor-123
    ... END:X-VENDOR-COMPONENT
    ... END:VCALENDAR
    ... """
    >>> cal = Calendar.from_ical(original)
    >>> regenerated = cal.to_ical()
    >>> # Custom component and its properties are preserved
    >>> b'X-VENDOR-COMPONENT' in regenerated
    True
    >>> b'X-VENDOR-PROP' in regenerated
    True

Component.from_ical() vs Calendar.from_ical()
==============================================

- **Component.from_ical()**: Standalone components, fragments
- **Calendar.from_ical()**: Complete .ics files, handles timezones

.. code-block:: pycon

    >>> from icalendar import Component, Calendar
    >>>
    >>> # Standalone custom component - use Component.from_ical()
    >>> standalone = b"BEGIN:X-MYCOMP\\r\\nEND:X-MYCOMP\\r\\n"
    >>> comp = Component.from_ical(standalone)
    >>>
    >>> # Complete calendar - use Calendar.from_ical()
    >>> calendar_data = b"""BEGIN:VCALENDAR
    ... VERSION:2.0
    ... BEGIN:X-MYCOMP
    ... END:X-MYCOMP
    ... END:VCALENDAR
    ... """
    >>> cal = Calendar.from_ical(calendar_data)

Advanced: Creating Custom Component Subclasses
===============================================

While the dynamic component creation works for most cases, you can create explicit component subclasses for custom components that need special behavior:

.. code-block:: python

    from icalendar import Component, ComponentFactory

    class XVendorComponent(Component):
        """Custom vendor-specific component with special behavior."""

        name = "X-VENDOR"

        def validate(self):
            """Custom validation logic."""
            required_props = ['UID', 'X-VENDOR-ID']
            for prop in required_props:
                if prop not in self:
                    raise ValueError(f"Missing required property: {prop}")

        def get_vendor_id(self):
            """Convenience method for vendor ID."""
            return self.get('X-VENDOR-ID')

    # Register with the factory
    factory = ComponentFactory()
    factory.add_component_class(XVendorComponent)

After registration, parsing ``BEGIN:X-VENDOR`` will use your custom class instead of the dynamic one.

RFC 5545 Compliance
===================

The icalendar library is fully compliant with RFC 5545 requirements for custom components:

- **Preserves unknown components**: Custom components are never silently dropped
- **Maintains data integrity**: All properties and subcomponents are preserved
- **Round-trip safe**: Parse → serialize → parse produces equivalent results
- **No special handling**: X-components and IANA-components are treated identically

The library implements a permissive approach: rather than rejecting unknown components, it preserves them while making them accessible through the same API as standard components.

Nested Custom Components
=========================

Custom components can contain standard components, and vice versa:

.. code-block:: pycon

    >>> from icalendar import Component, Event
    >>> # Custom component containing a standard event
    >>> ics_data = b"""BEGIN:X-CONTAINER
    ... SUMMARY:Container
    ... BEGIN:VEVENT
    ... UID:event-1
    ... DTSTART:20240101T120000Z
    ... SUMMARY:Event inside custom component
    ... END:VEVENT
    ... END:X-CONTAINER
    ... """
    >>> container = Component.from_ical(ics_data)
    >>> container.name
    'X-CONTAINER'
    >>> event = container.subcomponents[0]
    >>> event.name
    'VEVENT'
    >>> event['SUMMARY']
    'Event inside custom component'

Use Cases
=========

- Vendor extensions (proprietary features)
- Experimental/draft component types
- Legacy system support
- Data preservation during round-trips

Example
-------

.. code-block:: pycon

    >>> from icalendar import Calendar, Component
    >>> cal = Calendar()
    >>> cal.add('prodid', '-//My App//EN')
    >>> cal.add('version', '2.0')
    >>> custom = Component(name='X-MYAPP-SETTINGS')
    >>> custom.add('x-theme', 'dark')
    >>> cal.add_component(custom)
    >>> b'BEGIN:X-MYAPP-SETTINGS' in cal.to_ical()
    True

See Also
========

- :py:class:`icalendar.Component` - Base component class
- :py:class:`icalendar.cal.component_factory.ComponentFactory` - Component factory
- :py:meth:`icalendar.Component.from_ical` - Parse components
- :py:meth:`icalendar.Calendar.from_ical` - Parse calendars
- :rfc:`5545` - iCalendar specification
