# -*- coding: latin-1 -*-
"""

An example from the RFC 2445 spec.

    >>> from iCalendar import Calendar
    >>> cal = Calendar.from_string(open('groupscheduled.ics','rb').read())
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
    
"""

if __name__ == "__main__":
    import os.path, doctest, groupscheduled
    # import and test this file 
    doctest.testmod(groupscheduled)
