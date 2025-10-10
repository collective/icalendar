iCalendar utility
=================

To get more information about the command line interface, use the ``-h``
option::

    $ icalendar -h

view
----

To output a human readable summary of an event::

    $ icalendar myfile.ics

The output will look something like this::

    Organiser: Secretary <secretary@company.com>
    Attendees:
      John Doe <j.doe@company.com>
      Randy <boss@company.com>
    Summary: Yearly evaluation.
    When: Tue 14 Mar 2017 11:00-12:00
    Location: Randy's office
    Comment: Reminder.
    Description:

    Your yearly evaluation is scheduled for next Tuesday. Please be on time.

To use this in terminal based e-mail clients like mutt, add a new mime type (as
root)::

    # cat << EOF > /usr/lib/mime/packages/icalendar
    text/calendar; icalendar '%s'; copiousoutput; description=iCalendar text; priority=2
    EOF
    # update-mime
