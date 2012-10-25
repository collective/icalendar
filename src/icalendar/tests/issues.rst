======
ISSUES
======

Test for reported issues.

NOTE: not sure what should happen with fixed issues in here -> move them to
      appropriate test file or keep here, marked fixed as reference where case
      came from... ???
      -rnix


Basic Imports
=============

    >>> from icalendar import Event
    >>> from datetime import datetime
    >>> import pytz

Issue #64 - Event.to_ical() fails for unicode strings
=====================================================

FIXED - SEE BELOW

https://github.com/collective/icalendar/issues/64
by Prillan

This is pretty self explanatory

Non-unicode characters

    >>> event = Event()
    >>> event.add("dtstart", datetime(2012,9,3,0,0,0))
    >>> event.add("summary", u"abcdef")
    >>> event.to_ical()
    'BEGIN:VEVENT\r\nSUMMARY:abcdef\r\nDTSTART;VALUE=DATE-TIME:20120903T000000\r\nEND:VEVENT\r\n' 

Unicode characters

    >>> event = Event()
    >>> event.add("dtstart", datetime.now())
    >>> event.add("summary", u"åäö")
    >>> event.to_ical()
    'BEGIN:VEVENT\r\nSUMMARY:\xc3\x83\xc2\xa5\xc3\x83\xc2\xa4\xc3\x83\xc2\xb6\r\nDTSTART;VALUE=DATE-TIME:...\r\nEND:VEVENT\r\n'


Issue #58 - TZID on UTC DATE-TIMEs
==================================

FIXED - SEE BELOW

https://github.com/collective/icalendar/issues/58
By gregbaker

According to RFC 2445: "The TZID property parameter MUST NOT be applied to
DATE-TIME or TIME properties whose time values are specified in UTC."

But the module will produce them in cases like:

    >>> e = Event()
    >>> e.add('dtstart', pytz.utc.localize(datetime(2012,7,16,0,0,0)))
    >>> print e.to_ical()
    BEGIN:VEVENT
    DTSTART;VALUE=DATE-TIME:20120716T000000Z
    END:VEVENT
