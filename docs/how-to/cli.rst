======================
Command line interface
======================

This chapter describes how to use the command line interface (CLI) for icalendar.

The CLI consists of the ``icalendar`` command followed by arguments.


Help
====

To get information about all the commands, use the ``-h`` option.

.. code-block:: shell

    icalendar -h

View an event
=============

To view a readable summary of an event file that is in icalendar format, pass the name of the icalendar file to ``icalendar``.

.. code-block:: shell

    icalendar myfile.ics

The following is example output.

.. code-block:: text

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

Shell-based mail client
=======================

To use icalendar in terminal-based mail clients such as mutt, add a new MIME type as the root user as shown.

.. code-block:: shell

    cat << EOF > /usr/lib/mime/packages/icalendar
    text/calendar; icalendar '%s'; copiousoutput; description=iCalendar text; priority=2
    EOF
    update-mime
