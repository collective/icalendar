An example from the RFC 2445 spec::

  >>> from icalendar import Calendar
  >>> import os
  >>> directory = os.path.dirname(__file__)
  >>> cal = Calendar.from_ical(
  ...   open(os.path.join(directory, 'groupscheduled.ics'),'rb').read())
  >>> cal
  VCALENDAR({'VERSION': '2.0', 'PRODID': '-//RDU Software//NONSGML HandCal//EN'})

  >>> timezones = cal.walk('VTIMEZONE')
  >>> len(timezones)
  1

  >>> tz = timezones[0]
  >>> tz
  VTIMEZONE({'TZID': 'US-Eastern'})

  >>> std = tz.walk('STANDARD')[0]
  >>> std.decoded('TZOFFSETFROM')
  datetime.timedelta(-1, 72000)
