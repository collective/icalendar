=================
Custom components
=================

This chapter describes how to use custom components in icalendar.

icalendar automatically handles X-components and IANA-components not in :rfc:`5545`.

:rfc:`5545` defines two custom component types.

X-Components
    Vendor-specific components, for example, ``X-MYAPP-SETTINGS``.

IANA-Components
    IANA-registered components, but not in :rfc:`5545`.

icalendar preserves all custom components through dynamic component creation using :class:`~icalendar.cal.component_factory.ComponentFactory`.


Parse custom components
=======================

Parse custom components using either :meth:`Component.from_ical() <icalendar.cal.component.Component.from_ical>` or :meth:`Calendar.from_ical() <icalendar.cal.calendar.Calendar.from_ical>`.


``Component.from_ical()``
-------------------------

Parse any component type, including custom ones.
The following example shows how to parse a component, then display its name and ``SUMMARY``.

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
    >>> str(component["SUMMARY"])
    'Custom component example'


``Calendar.from_ical()``
------------------------

Parse a calendar containing custom components.
The following example shows how to parse a component, get its subcomponents, then display its name and ``UID``.

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
    >>> str(custom["UID"])
    'custom-1'


Access custom components
========================

Custom components work exactly like standard components.
The following example shows how to access a custom component to display its name and other attributes.

.. code-block:: pycon

    >>> from icalendar import Component
    >>> # Create custom component using factory
    >>> MyComp = Component.get_component_class("MYCOMP")
    >>> comp = MyComp()
    >>> comp.name
    'MYCOMP'
    >>>
    >>> # Add properties
    >>> comp.add("summary", "Test Summary")
    >>> comp.add("x-custom-field", "Custom Value")
    >>>
    >>> # Access properties
    >>> str(comp["SUMMARY"])
    'Test Summary'
    >>> str(comp.get("X-CUSTOM-FIELD"))
    'Custom Value'
    >>>
    >>> # Add subcomponents
    >>> from icalendar import Event
    >>> event = Event()
    >>> event.add("uid", "123")
    >>> comp.add_component(event)
    >>> len(comp.subcomponents)
    1


Round-trip preservation
=======================

Custom components are fully preserved during round-trip parsing.
The following example demonstrates this feature.

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
    >>> b"X-VENDOR-COMPONENT" in regenerated
    True
    >>> b"X-VENDOR-PROP" in regenerated
    True


Which ``from_ical()``?
======================

Use ``Component.from_ical()`` for standalone components and fragments.

Use ``Calendar.from_ical()`` for complete iCalendar files.
It also handles timezones.

The following example shows the different usage of both methods.

.. code-block:: pycon

    >>> from icalendar import Component, Calendar
    >>>
    >>> # Standalone custom component - use Component.from_ical()
    >>> standalone = b"""BEGIN:X-MYCOMP
    ... UID:123
    ... END:X-MYCOMP
    ... """
    >>> comp = Component.from_ical(standalone)
    >>> comp.name
    'X-MYCOMP'
    >>>
    >>> # Complete calendar - use Calendar.from_ical()
    >>> calendar_data = b"""BEGIN:VCALENDAR
    ... VERSION:2.0
    ... PRODID:-//Test//EN
    ... BEGIN:X-MYCOMP
    ... UID:123
    ... END:X-MYCOMP
    ... END:VCALENDAR
    ... """
    >>> cal = Calendar.from_ical(calendar_data)
    >>> len(cal.subcomponents)
    1


Register custom component classes
==================================

Register custom component classes with special behavior.
The following example shows how to create and register a custom component with validation and helper methods.

.. code-block:: python

    from icalendar import Component

    class XAcmeComponent(Component):
        """Custom ACME component with validation."""

        name = "X-ACME"

        def validate(self):
            """Validate required properties."""
            required = ["UID", "X-ACME-ID"]
            for prop in required:
                if prop not in self:
                    raise ValueError(f"Missing {prop}")

        def get_acme_id(self):
            """Get ACME ID."""
            return self.get("X-ACME-ID")

    # Register the component
    Component.register(XAcmeComponent)

After registration, parsing ``BEGIN:X-ACME`` uses your custom class:

.. code-block:: pycon

    >>> from icalendar import Component
    >>> class XAcmeComponent(Component):
    ...     """Custom ACME component with validation."""
    ...     name = "X-ACME"
    ...     def validate(self):
    ...         """Validate required properties."""
    ...         required = ["UID", "X-ACME-ID"]
    ...         for prop in required:
    ...             if prop not in self:
    ...                 raise ValueError(f"Missing {prop}")
    ...     def get_acme_id(self):
    ...         """Get ACME ID."""
    ...         return self.get("X-ACME-ID")
    >>> Component.register(XAcmeComponent)
    >>> ical_data = b"""BEGIN:X-ACME
    ... UID:123
    ... X-ACME-ID:acme-1
    ... END:X-ACME
    ... """
    >>> comp = Component.from_ical(ical_data)
    >>> comp.validate()
    >>> str(comp.get_acme_id())
    'acme-1'


:rfc:`5545` compliance
======================

The icalendar library is fully compliant with :rfc:`5545` requirements for custom components.

Preserves unknown components
    Custom components are never dropped.

Maintains data integrity
    All properties and subcomponents are preserved.

Round-trip safe
    Parse to serialize, and back to parse, produces equivalent results.

No special handling
    X-components and IANA-components are treated identically.

icalendar implements a permissive approach.
Rather than rejecting unknown components, it preserves them while making them accessible through the same API as standard components.


Nested custom components
========================

Custom components can contain standard components, and vice versa.

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
    >>> str(event["SUMMARY"])
    'Event inside custom component'


Use cases
=========

Custom components extend the functionality beyond icalendar's core.
Use cases include the following:

-   vendor extensions and proprietary features
-   experimental or draft component types
-   legacy system support
-   data preservation during round-trips

The following example shows how to add a feature for a calendar, where an application supports dark mode in its theme.

.. code-block:: pycon

    >>> from icalendar import Calendar, Component
    >>> cal = Calendar()
    >>> cal.add("prodid", "-//My App//EN")
    >>> cal.add("version", "2.0")
    >>> # Create custom component using factory
    >>> CustomSettings = Component.get_component_class("X-MYAPP-SETTINGS")
    >>> custom = CustomSettings()
    >>> custom.add("uid", "settings-1")
    >>> custom.add("x-theme", "dark")
    >>> cal.add_component(custom)
    >>> b"BEGIN:X-MYAPP-SETTINGS" in cal.to_ical()
    True


Related content
===============

:class:`~icalendar.cal.component.Component`
    Base component class

:class:`icalendar.cal.component_factory.ComponentFactory`
    Component factory

:meth:`Component.from_ical <icalendar.cal.component.Component.from_ical>`
    Parse components

:meth:`Calendar.from_ical <icalendar.cal.calendar.Calendar.from_ical>`
    Parse calendars

:rfc:`5545`
    iCalendar specification
