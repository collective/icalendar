Enumerations in :mod:`icalendar.enums` now accept case-insensitive values.
:class:`~icalendar.enums.PARTSTAT` and the other case-insensitive enums can be
created from any casing, so ``PARTSTAT("needs-action")``,
``PARTSTAT("NEEDS-ACTION")``, and ``PARTSTAT.NEEDS_ACTION`` are the same member.
I used DeepSeek V4.1 Flash to assist me with this change. @chaitanya-y20
