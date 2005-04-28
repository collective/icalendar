============================
iCalendar package for Python
============================

The iCalendar package is a parser/generator of iCalender files for use
with Python. It follows the RFC 2445 (iCalendar) specification, which
can be found here:

http://www.ietf.org/rfc/rfc2445.txt

Introduction
============
    
I (Max M) have often needed to parse and generate iCalendar
files. Finally I got tired of writing ad-hoc tools.
    
So this is my attempt at making an iCalendar package for Python. The
inspiration has come from the email package in the standard lib, which
I think is pretty simple, yet efficient and powerful.

The aim is to make a package that is fully compliant to RFC 2445, well
designed, simple to use and well documented.

Look in doc/example.txt for introductory doctests and explanations.
    
All modules and classes have doctests that shows how they work, so it
is all pretty well documented. There is also an interfaces.py file
which describe the API in src/icalendar.
    
It can generate and parse iCalender files, and can easily be used as
is.
    
But it does need a bit more polish before i will considder it
finished. I would say that it's about 95% done.
    
Examples
========

To open and parse a file::
    
  >>> from iCalendar import Calendar, Event
  >>> cal = Calendar.from_string(open('test.ics','rb').read())
  >>> cal
  VCALENDAR({'VERSION': '2.0', 'METHOD': 'Request', 'PRODID': '-//My product//mxm.dk/'})
    
  >>> for component in cal.walk():
  ...     component.name
  'VCALENDAR'
  'VEVENT'
  'VEVENT'
        
To create a calendar and write it to disk::
        
  >>> cal = Calendar()
  >>> from datetime import datetime
  >>> from iCalendar import UTC # timezone
  >>> cal.add('prodid', '-//My calendar product//mxm.dk//')
  >>> cal.add('version', '2.0')
        
  >>> event = Event()
  >>> event.add('summary', 'Python meeting about calendaring')
  >>> event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=UTC()))
  >>> event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=UTC()))
  >>> event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=UTC()))
  >>> event['uid'] = '20050115T101010/27346262376@mxm.dk'
  >>> event.add('priority', 5)
        
  >>> cal.add_component(event)
        
  >>> f = open('example.ics', 'wb')
  >>> f.write(cal.as_string())
  >>> f.close()

Dependencies
============
    
It is dependent on the datetime package, so it requires Python >=
2.3. There are no other dependencies.

Mailing list
============

If you have any comments or feedback on the module, please use the iCalendar
mailing list. You can subscribe to it here:
   
http://codespeak.net/mailman/listinfo/icalendar-dev

We would love to hear use cases, or get ideas for improvements.

There is also a checkins mailing list, if you want to follow development:

http://codespeak.net/mailman/listinfo/icalendar-checkins

Download
========

Get the latest version from the download page.

License
=======

LGPL. See LICENSE.txt for details.
