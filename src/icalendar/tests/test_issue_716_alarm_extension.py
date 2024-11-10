"""Test the alarm classification.

Events can have alarms.
Alarms can be in this state:

- active - the user wants the alarm to pop up
- acknowledged - the user no longer wants the alarm
- snoozed - the user moved that alarm to another time

The alarms can only work on the properties of the event like
DTSTART, DTEND and DURATION.

"""