



Issue 64
========

Event.to_ical() fails for unicode strings

https://github.com/collective/icalendar/issues/64
by Prillan

This is pretty self explanatory

Non-unicode characters

    >>> from icalendar import Event
    >>> from datetime import datetime

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
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "icalendar\cal.py", line 481, in to_ical
        return self.content_lines().to_ical()
      File "icalendar\cal.py", line 476, in content_lines
        contentlines.append(Contentline.from_parts((name, params, values)))
      File "icalendar\parser.py", line 424, in from_parts
        repr(values)))
    ValueError: Property: 'SUMMARY' Wrong values "Parameters({})" or "vText(u'\xe5\xe4\xf6')"


