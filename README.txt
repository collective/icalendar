iCalendar package for Python

The iCalendar package is a parser/generator of iCalender files for use with 
Python. It follows the RFC 2445 spec.


Summary
    
    I have often needed to parse and generate iCalendar files. Finally I got 
    tired of writing ad-hoc tools.
    
    So this is my attempt at making an iCalendar package for Python. The 
    inspiration has come from the email package in the standard lib, which I 
    think is pretty simple, yet efficient and powerfull.

    The aim is to make a package that is fully compliant to RFC 2445, well 
    designed, simple to use and well documented.

    Look in
    "doc/example.py":http://www.mxm.dk/products/public/ical/example.py/file_view
    for introductory doctests and explanations.
    
    All modules and classes have doctest that shows how they work, so it is all 
    pretty well documented.
    
    It can generate and parse iCalender files, and can easily be used as is.
    
    But it does needs a bit more polish before i will considder it finished. I 
    would say that it's about 95% done.
    
Examples

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
        
    To create a calendar and write it to disc::
    
    
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


Note!

    This is the first public release, so it is most likely buggy in some degree. 
    But it is usable for production.
    
    It is dependent on the datetime package, so it requires Python >= 2.2

Feedback/contact

    If you have any comments or feedback on the module, please contact me at: 
    "maxm@mxm.dk":maxm@mxm.dk
    
    I would love to hear use cases, or get ideas for improvements.

Download

    Get the latest version from the
    "download page":http://www.mxm.dk/products/public/ical/downloads

License

    LGPL