A small example::

  >>> from icalendar import Calendar
  >>> import os
  >>> directory = os.path.dirname(__file__)
  >>> cal = Calendar.from_ical(
  ...   open(os.path.join(directory, 'small.ics'),'rb').read())
  >>> cal
  VCALENDAR({'VERSION': vText(u'2.0'), 'METHOD': vText(u'Request'), 'PRODID': vText(u'-//My product//mxm.dk/')})

  >>> for component in cal.walk():
  ...     component.name
  'VCALENDAR'
  'VEVENT'
  'VEVENT'

  >>> cal['prodid']
  vText(u'-//My product//mxm.dk/')

  >>> cal.decoded('prodid')
  u'-//My product//mxm.dk/'

  >>> first_event = cal.walk('vevent')[0]
  >>> first_event['description'][:75]
  u'This is a very long description that will be folded This is a very long des'

  >>> first_event['summary']
  vText(u'A second event')
