iCalendar package
=================

This package is used for parsing and generating iCalendar files following the
standard in RFC 5545.

It should be fully compliant, but it is possible to generate and parse invalid
files if you really want to.

Compatibility
-------------

This package is compatible with the following standards:

- :rfc:`2445` - obsoleted by :rfc:`5545`
- :rfc:`5545` - Internet Calendaring and Scheduling Core Object Specification (iCalendar)
- :rfc:`6868` - Parameter Value Encoding in iCalendar and vCard
- :rfc:`7529` - Non-Gregorian Recurrence Rules in the Internet Calendaring and Scheduling Core Object Specification (iCalendar)
- :rfc:`9074` - "VALARM" Extensions for iCalendar

We do not claim compatibility to the following RFCs. They might work though.

- :rfc:`7953` - Calendar Availability
- :rfc:`7986` - New Properties for iCalendar
- :rfc:`9073` - Event Publishing Extensions to iCalendar
- :rfc:`9253` - Support for iCalendar Relationships

iCalendar file structure
------------------------

An iCalendar file is a text file with UTF-8 character encoding in a special format.

It consists of **content lines**,
with each content line defining a property that has 3 parts: name, parameters, and values. Parameters are optional.

Example 1: a simple content line, with only name and value.

.. code-block:: text

    BEGIN:VCALENDAR

Example 2: a content line with parameters.

.. code-block:: text

    ATTENDEE;CN=Max Rasmussen;ROLE=REQ-PARTICIPANT:MAILTO:example@example.com

The parts in this example are the following.

.. code-block:: text

    Name:   ATTENDEE
    Params: CN=Max Rasmussen;ROLE=REQ-PARTICIPANT
    Value:  MAILTO:example@example.com

For long content lines, iCalendar usually "folds" them to less than 75 characters.

On a higher level, you can think of iCalendar files' structure as having components and subcomponents.

A component will have properties with values. The values
have special types, like integer, text, and datetime. These values are
encoded in a special text format in an iCalendar file. This package contains methods for converting to and from these encodings.

Example 1: this is a VCALENDAR component representing a calendar.

.. code-block:: text

    BEGIN:VCALENDAR
    ... vcalendar properties ...
    END:VCALENDAR

Example 2: The most frequent subcomponent to a VCALENDAR component is a VEVENT. This is a VCALENDAR component with a nested VEVENT subcomponent.

.. code-block:: text

    BEGIN:VCALENDAR
    ... vcalendar properties ...
    BEGIN:VEVENT
    ... vevent properties ...
    END:VEVENT
    END:VCALENDAR


Components
----------

The remaining code snippets in the documentation will use the following important imports.

.. code-block:: pycon

    >>> from icalendar import Calendar, Event

Components are like (Case Insensitive) dicts. So if you want to set a property
you do it like this. The calendar is a component.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal['dtstart'] = '20050404T080000'
    >>> cal['summary'] = 'Python meeting about calendaring'
    >>> for k,v in cal.items():
    ...     k,v
    ('DTSTART', '20050404T080000')
    ('SUMMARY', 'Python meeting about calendaring')

NOTE: the recommended way to add components to the calendar is to
create the subcomponent and add it via ``Calendar.add``! The example above adds a
string, but not a ``vText`` component.


You can generate a string for a file with the ``to_ical()`` method.

.. code-block:: pycon

    >>> cal.to_ical()
    b'BEGIN:VCALENDAR\r\nDTSTART:20050404T080000\r\nSUMMARY:Python meeting about calendaring\r\nEND:VCALENDAR\r\n'

The rendered view is easier to read.

.. code-block:: pycon

    BEGIN:VCALENDAR
    DTSTART:20050404T080000
    SUMMARY:Python meeting about calendaring
    END:VCALENDAR

So, let's define a function so we can easily display to_ical() output.

.. code-block:: pycon

    >>> def display(cal):
    ...    return cal.to_ical().decode("utf-8").replace('\r\n', '\n').strip()

You can set multiple properties like this.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal['attendee'] = ['MAILTO:maxm@mxm.dk','MAILTO:test@example.com']
    >>> print(display(cal))
    BEGIN:VCALENDAR
    ATTENDEE:MAILTO:maxm@mxm.dk
    ATTENDEE:MAILTO:test@example.com
    END:VCALENDAR

If you don't want to care about whether a property value is a list or
a single value, just use the add() method. It will automatically
convert the property to a list of values if more than one value is
added. Here is an example.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal.add('attendee', 'MAILTO:maxm@mxm.dk')
    >>> cal.add('attendee', 'MAILTO:test@example.com')
    >>> print(display(cal))
    BEGIN:VCALENDAR
    ATTENDEE:MAILTO:maxm@mxm.dk
    ATTENDEE:MAILTO:test@example.com
    END:VCALENDAR

Note: this version doesn't check for compliance, so you should look in
the RFC 5545 spec for legal properties for each component, or look in
the icalendar/calendar.py file, where it is at least defined for each
component.


Subcomponents
-------------

Any component can have subcomponents. Eg. inside a calendar there can
be events.  They can be arbitrarily nested. First by making a new
component.

.. code-block:: pycon

    >>> event = Event()
    >>> event['uid'] = '42'
    >>> event['dtstart'] = '20050404T080000'

And then appending it to a "parent".

.. code-block:: pycon

    >>> cal.add_component(event)
    >>> print(display(cal))
    BEGIN:VCALENDAR
    ATTENDEE:MAILTO:maxm@mxm.dk
    ATTENDEE:MAILTO:test@example.com
    BEGIN:VEVENT
    DTSTART:20050404T080000
    UID:42
    END:VEVENT
    END:VCALENDAR

Subcomponents are appended to the subcomponents property on the component.

.. code-block:: pycon

    >>> cal.subcomponents
    [VEVENT({'UID': '42', 'DTSTART': '20050404T080000'})]


Value types
-----------

Property values are utf-8 encoded strings.

This is impractical if you want to use the data for further
computation. The datetime format for example looks like this:
'20050404T080000'. But the package makes it simple to parse and
generate iCalendar formatted strings.

Basically you can make the add() method do the thinking, or you can do it
yourself.

To add a datetime value, you can use Pythons built in datetime types,
and the set the encode parameter to true, and it will convert to the
type defined in the spec.

.. code-block:: pycon

    >>> from datetime import datetime
    >>> cal.add('dtstart', datetime(2005,4,4,8,0,0))
    >>> cal['dtstart'].to_ical()
    b'20050404T080000'

If that doesn't work satisfactorily for some reason, you can also do it
manually.

In 'icalendar.prop', all the iCalendar data types are defined. Each
type has a class that can parse and encode the type.

So if you want to do it manually.

.. code-block:: pycon

    >>> from icalendar import vDatetime
    >>> now = datetime(2005,4,4,8,0,0)
    >>> vDatetime(now).to_ical()
    b'20050404T080000'

So the drill is to initialise the object with a python built in type,
and then call the "to_ical()" method on the object. That will return an
ical encoded string.

You can do it the other way around too. To parse an encoded string, just call
the "from_ical()" method, and it will return an instance of the corresponding
Python type.

.. code-block:: pycon

    >>> vDatetime.from_ical('20050404T080000')
    datetime.datetime(2005, 4, 4, 8, 0)

    >>> vDatetime.from_ical('20050404T080000Z')
    datetime.datetime(2005, 4, 4, 8, 0, tzinfo=ZoneInfo(key='UTC'))

You can also choose to use the decoded() method, which will return a decoded
value directly.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> cal.add('dtstart', datetime(2005,4,4,8,0,0))
    >>> cal['dtstart'].to_ical()
    b'20050404T080000'
    >>> cal.decoded('dtstart')
    datetime.datetime(2005, 4, 4, 8, 0)


Property parameters
-------------------

Property parameters are automatically added, depending on the input value. For
example, for date/time related properties, the value type and timezone
identifier (if applicable) are automatically added here.

.. code-block:: pycon

    >>> import zoneinfo
    >>> event = Event()
    >>> event.add('dtstart', datetime(2010, 10, 10, 10, 0, 0,
    ...                               tzinfo=zoneinfo.ZoneInfo("Europe/Vienna")))

    >>> lines = event.to_ical().splitlines()
    >>> assert (
    ...     b"DTSTART;TZID=Europe/Vienna:20101010T100000"
    ...     in lines)


You can also add arbitrary property parameters by passing a parameters
dictionary to the add method like so.

.. code-block:: pycon

    >>> event = Event()
    >>> event.add('X-TEST-PROP', 'tryout.',
    ...           parameters={'prop1':'val1', 'prop2':'val2'})
    >>> lines = event.to_ical().splitlines()
    >>> assert b"X-TEST-PROP;PROP1=val1;PROP2=val2:tryout." in lines


Example
-------

Here is an example generating a complete iCal calendar file with a
single event that can be loaded into the Mozilla calendar.

Initialize the calendar.

.. code-block:: pycon

    >>> cal = Calendar()
    >>> from datetime import datetime
    >>> import zoneinfo

Some properties are required to be compliant.

.. code-block:: pycon

    >>> cal.add('prodid', '-//My calendar product//mxm.dk//')
    >>> cal.add('version', '2.0')

We need at least one subcomponent for a calendar to be compliant.

.. code-block:: pycon

    >>> event = Event()
    >>> event.add('summary', 'Python meeting about calendaring')
    >>> event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=zoneinfo.ZoneInfo("UTC")))
    >>> event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=zoneinfo.ZoneInfo("UTC")))
    >>> event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=zoneinfo.ZoneInfo("UTC")))

A property with parameters. Notice that they are an attribute on the value.

.. code-block:: pycon

    >>> from icalendar import vCalAddress, vText
    >>> organizer = vCalAddress('MAILTO:noone@example.com')

Automatic encoding is not yet implemented for parameter values, so you
must use the 'v*' types you can import from the icalendar package
(they're defined in ``icalendar.prop``).

.. code-block:: pycon

    >>> organizer.params['cn'] = vText('Max Rasmussen')
    >>> organizer.params['role'] = vText('CHAIR')
    >>> event['organizer'] = organizer
    >>> event['location'] = vText('Odense, Denmark')

    >>> event['uid'] = '20050115T101010/27346262376@mxm.dk'
    >>> event.add('priority', 5)

    >>> attendee = vCalAddress('MAILTO:maxm@example.com')
    >>> attendee.params['cn'] = vText('Max Rasmussen')
    >>> attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    >>> event.add('attendee', attendee, encode=0)

    >>> attendee = vCalAddress('MAILTO:the-dude@example.com')
    >>> attendee.params['cn'] = vText('The Dude')
    >>> attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    >>> event.add('attendee', attendee, encode=0)

Add the event to the calendar.

.. code-block:: pycon

    >>> cal.add_component(event)

By extending the event with subcomponents, you can create multiple alarms.

.. code-block:: pycon

    >>> from icalendar import Alarm
    >>> from datetime import timedelta
    >>> alarm_1h_before = Alarm()
    >>> alarm_1h_before.add('action', 'DISPLAY')
    >>> alarm_1h_before.add('trigger', timedelta(hours=-1))
    >>> alarm_1h_before.add('description', 'Reminder: Event in 1 hour')
    >>> event.add_component(alarm_1h_before)

    >>> alarm_24h_before = Alarm()
    >>> alarm_24h_before.add('action', 'DISPLAY')
    >>> alarm_24h_before.add('trigger', timedelta(hours=-24))
    >>> alarm_24h_before.add('description', 'Reminder: Event in 24 hours')
    >>> event.add_component(alarm_24h_before)

Or even recurrence, either from a dictionary or a string.
Note that if you want to add the reccurence rule from a string, you must use the ``vRecur`` property.
Otherwise the rule will be escaped, making it invalid.

.. code-block:: pycon

    >>> event.add('rrule', {'freq': 'daily'})

Write to disk.

.. code-block:: pycon

    >>> import tempfile, os
    >>> directory = tempfile.mkdtemp()
    >>> f = open(os.path.join(directory, 'example.ics'), 'wb')
    >>> f.write(cal.to_ical())
    733
    >>> f.close()

Print out the calendar.

.. code-block:: pycon

    >>> print(cal.to_ical().decode('utf-8')) # doctest: +NORMALIZE_WHITESPACE
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//My calendar product//mxm.dk//
    BEGIN:VEVENT
    SUMMARY:Python meeting about calendaring
    DTSTART:20050404T080000Z
    DTEND:20050404T100000Z
    DTSTAMP:20050404T001000Z
    UID:20050115T101010/27346262376@mxm.dk
    RRULE:FREQ=DAILY
    ATTENDEE;CN="Max Rasmussen";ROLE=REQ-PARTICIPANT:MAILTO:maxm@example.com
    ATTENDEE;CN="The Dude";ROLE=REQ-PARTICIPANT:MAILTO:the-dude@example.com
    LOCATION:Odense\, Denmark
    ORGANIZER;CN="Max Rasmussen";ROLE=CHAIR:MAILTO:noone@example.com
    PRIORITY:5
    BEGIN:VALARM
    ACTION:DISPLAY
    DESCRIPTION:Reminder: Event in 1 hour
    TRIGGER:-PT1H
    END:VALARM
    BEGIN:VALARM
    ACTION:DISPLAY
    DESCRIPTION:Reminder: Event in 24 hours
    TRIGGER:-P1D
    END:VALARM
    END:VEVENT
    END:VCALENDAR
    <BLANKLINE>

More documentation
==================

Have a look at the `tests <https://github.com/collective/icalendar/tree/main/src/icalendar/tests>`__ of this package to get more examples.
All modules and classes docstrings, which document how they work.
