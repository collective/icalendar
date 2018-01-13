iCalendar utility
=================

To get more information about the command line interface, use the ``-h``
option::

    $ icalendar -h

view
----

Use the ``view`` subcommand for a human readable summary of an event::

    $ icalendar view myfile.ics

To use this in terminal based e-mail clients like mutt, add a new mime type (as
root)::

    # cat << EOF > /usr/lib/mime/packages/icalendar
    text/calendar; icalendar view '%s'; copiousoutput; description=iCalendar text; priority=2
    EOF
    # update-mime
