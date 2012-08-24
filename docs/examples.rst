========
Examples
========

To open and parse a file::

  >>> from icalendar import Calendar, Event
  >>> cal = Calendar.from_ical(open('test.ics','rb').read())
  >>> cal
  VCALENDAR({'VERSION': vText(u'2.0'), 'METHOD': vText(u'Request'), 'PRODID': vText(u'-//My product//mxm.dk/')})

  >>> for component in cal.walk():
  ...     component.name
  'VCALENDAR'
  'VEVENT'
  'VEVENT'

To create a calendar and write it to disk::

  >>> cal = Calendar()
  >>> from datetime import datetime
  >>> cal.add('prodid', '-//My calendar product//mxm.dk//')
  >>> cal.add('version', '2.0')

  >>> import pytz
  >>> event = Event()
  >>> event.add('summary', 'Python meeting about calendaring')
  >>> event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=pytz.utc))
  >>> event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=pytz.utc))
  >>> event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=pytz.utc))
  >>> event['uid'] = '20050115T101010/27346262376@mxm.dk'
  >>> event.add('priority', 5)

  >>> cal.add_component(event)

  >>> f = open('example.ics', 'wb')
  >>> f.write(cal.to_ical())
  >>> f.close()

More documentation
==================

Have a look at the doctests in the tests directory of the package to get more
examples. All modules and classes also have doctests that show how they work.
There is also an `interfaces.py` file which describes the API.
