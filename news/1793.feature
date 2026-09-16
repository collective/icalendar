Invalid UTF-8 calendar bytes now raise :exc:`~icalendar.error.InvalidCalendar`
instead of being silently replaced. Pass ``encoding`` to parse legacy calendar
files with a known encoding, or pass ``errors="replace"`` to explicitly retain
the previous replacement behavior. See :issue:`1793`.