An example from the RFC 2445 spec::

  >>> from icalendar import Calendar
  >>> import os
  >>> directory = os.path.dirname(__file__)
  >>> cal = Calendar.from_ical(
  ...   open(os.path.join(directory, 'groupscheduled.ics'),'rb').read())
  >>> cal
  VCALENDAR({'VERSION': vText(u'2.0'), 'PRODID': vText(u'-//RDU Software//NONSGML HandCal//EN')})

  >>> timezones = cal.walk('VTIMEZONE')
  >>> len(timezones)
  1

  >>> tz = timezones[0]
  >>> tz
  VTIMEZONE({'TZID': vText(u'US-Eastern')})

  >>> std = tz.walk('STANDARD')[0]
  >>> std.decoded('TZOFFSETFROM')
  datetime.timedelta(-1, 72000)
