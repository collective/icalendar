# -*- coding: latin-1 -*-
"""

A small example

    >>> from iCalendar import Calendar
    >>> cal = Calendar.from_string(open('test.ics','rb').read())
    >>> cal
    VCALENDAR({'VERSION': '2.0', 'METHOD': 'Request', 'PRODID': '-//My product//mxm.dk/'})

    >>> for component in cal.walk():
    ...     component.name
    'VCALENDAR'
    'VEVENT'
    'VEVENT'
    
    >>> cal['prodid']
    '-//My product//mxm.dk/'
    
    >>> cal.decoded('prodid')
    u'-//My product//mxm.dk/'
    
    >>> first_event = cal.walk('vevent')[0]
    >>> first_event['description'][:75]
    'This is a very long description that will be folded This is a very long des'

    >>> first_event['summary']
    'A second event'
    
"""

if __name__ == "__main__":
    import os.path, doctest, test
    # import and test this file 
    doctest.testmod(test)
