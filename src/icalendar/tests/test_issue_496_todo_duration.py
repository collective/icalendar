"""``Todo.duration`` for the cases RFC 4791 covers but RFC 5545 leaves open.

RFC 5545 constrains which of ``DTSTART``, ``DUE`` and ``DURATION`` may appear
together in a ``VTODO``, but it never says what the duration of a task *is*
when ``DTSTART`` is missing.  :rfc:`4791`, section 9.9, does: its
``CALDAV:time-range`` table defines, for every combination of ``DTSTART``,
``DURATION``, ``DUE``, ``COMPLETED`` and ``CREATED``, which time range a
``VTODO`` occupies.  Read as a definition of start and end, the table gives:

===========================  ==========================================
Properties present           Time occupied by the task
===========================  ==========================================
``DTSTART`` + ``DURATION``   ``DTSTART`` .. ``DTSTART+DURATION``
``DTSTART`` + ``DUE``        ``DTSTART`` .. ``DUE``
``DTSTART``                  the instant ``DTSTART`` (zero duration)
``DUE``                      the instant ``DUE`` (zero duration)
``COMPLETED`` + ``CREATED``  ``CREATED`` .. ``COMPLETED``
``COMPLETED``                the instant ``COMPLETED`` (zero duration)
``CREATED``                  ``CREATED`` .. indefinite
nothing                      indefinite
===========================  ==========================================

``DURATION`` without ``DTSTART`` has no row of its own: it is invalid per
RFC 5545, and RFC 4791 does not consider it.  icalendar nevertheless returns it
(https://github.com/collective/icalendar/issues/867), which is the precedent
for deriving a duration without a ``DTSTART`` at all.

The first three rows work today and are covered by
``test_issue_867_todo_duration_fix.py`` and
``test_issue_662_component_properties.py``; they are not repeated here.  Every
remaining row raises :exc:`~icalendar.error.IncompleteComponent` instead.

See https://github.com/collective/icalendar/issues/496

"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from icalendar import Todo
from icalendar.error import IncompleteComponent

UTC = timezone.utc


# ---------------------------------------------------------------------------
# Not working: DUE without DTSTART.
#
# RFC 4791: | N | N | Y | * | * | (start < DUE) AND (end >= DUE)
# The task occupies the instant DUE, so its duration is zero.
# ---------------------------------------------------------------------------


def test_due_without_dtstart_is_an_instant():
    """``DUE`` alone gives a zero duration, not an error."""
    todo = Todo()
    todo.end = datetime(2026, 1, 1, 12, tzinfo=UTC)
    assert todo.duration == timedelta(0)


def test_due_date_without_dtstart_is_an_instant():
    """``DUE`` alone as a date value gives a zero duration too.

    RFC 4791 has no date/datetime column for ``VTODO``, though its ``VEVENT``
    and ``VJOURNAL`` tables both give a date value an effective ``P1D``.  Zero
    is chosen here for consistency with
    https://github.com/collective/icalendar/issues/898, which made a
    date-valued and a datetime-valued ``DTSTART`` behave alike for a ``Todo``.
    """
    todo = Todo()
    todo.end = date(2026, 1, 1)
    assert todo.duration == timedelta(0)


def test_due_without_dtstart_starts_at_due():
    """With only ``DUE``, the task starts and ends at ``DUE``.

    IMPORTANT: this needs a decision to be made.  Today a ``Todo``
    without ``DTSTART`` raises on ``.start``, and
    ``test_issue_662_component_properties.py`` pins that contract.
    The assertion on ``DTSTART`` is there so the question cannot be
    answered by writing a ``DTSTART`` property into the component.

    """
    due = datetime(2026, 1, 1, 12, tzinfo=UTC)
    todo = Todo()
    todo.end = due
    assert todo.start == due
    assert todo.end == due
    assert "DTSTART" not in todo


def test_due_without_dtstart_parsed_from_ical():
    """The same, for a task that came off the wire."""
    todo = Todo.from_ical(
        "BEGIN:VTODO\r\n"
        "UID:due-only\r\n"
        "DTSTAMP:20260101T120000Z\r\n"
        "DUE:20260101T120000Z\r\n"
        "SUMMARY:Hand in the tax return\r\n"
        "END:VTODO\r\n"
    )
    assert todo.duration == timedelta(0)


# ---------------------------------------------------------------------------
# Working as decided: DUE before DTSTART.
#
# RFC 5545 section 3.8.2.3 requires DUE to be *later in time* than DTSTART -
# strictly later, so not even DUE == DTSTART is valid.  (RFC 2445, which
# RFC 4791 quotes, said "equal to or after".)  A task with DUE before DTSTART
# is therefore invalid data, and issue #496 suggested clamping it to zero.
# https://github.com/collective/icalendar/issues/999 decided otherwise: a
# negative duration is allowed for a task, to say that it is overdue.  These
# two tests pin that decision for the DUE/DTSTART pair, where it was so far
# only tested through the DURATION property.
# ---------------------------------------------------------------------------


def test_due_before_dtstart_is_negative():
    """A task with ``DUE`` before ``DTSTART`` keeps its negative duration."""
    todo = Todo()
    todo.start = datetime(2026, 1, 1, 12, tzinfo=UTC)
    todo.end = datetime(2026, 1, 1, 11, tzinfo=UTC)
    assert todo.duration == timedelta(hours=-1)


def test_due_before_dtstart_date_values_is_negative():
    """The same with date values."""
    todo = Todo()
    todo.start = date(2026, 1, 2)
    todo.end = date(2026, 1, 1)
    assert todo.duration == timedelta(days=-1)


# ---------------------------------------------------------------------------
# Not working: the CREATED / COMPLETED fallback.
#
# RFC 4791: | N | N | N | Y | Y | spans CREATED .. COMPLETED
#           | N | N | N | Y | N | the instant COMPLETED
#
# The RFC condition is written with OR on both sides, so it is really
# min .. max rather than CREATED .. COMPLETED.  A task completed before it was
# created is malformed; the ordered reading is deliberate here, and the
# disordered case is left undecided.
# ---------------------------------------------------------------------------


def test_created_and_completed():
    """Without any of ``DTSTART``/``DUE``/``DURATION``, the task spans ``CREATED`` to ``COMPLETED``."""
    todo = Todo()
    todo.add("CREATED", datetime(2026, 1, 1, 10, tzinfo=UTC))
    todo.add("COMPLETED", datetime(2026, 1, 1, 12, tzinfo=UTC))
    assert todo.duration == timedelta(hours=2)


def test_completed_without_created_is_an_instant():
    """``COMPLETED`` alone gives a zero duration."""
    todo = Todo()
    todo.add("COMPLETED", datetime(2026, 1, 1, 12, tzinfo=UTC))
    assert todo.duration == timedelta(0)


def test_dtstart_wins_over_created_and_completed():
    """``DTSTART``/``DUE`` take precedence over ``CREATED``/``COMPLETED``."""
    todo = Todo()
    todo.start = datetime(2026, 1, 1, 12, tzinfo=UTC)
    todo.end = datetime(2026, 1, 1, 13, tzinfo=UTC)
    todo.add("CREATED", datetime(2025, 1, 1, 10, tzinfo=UTC))
    todo.add("COMPLETED", datetime(2026, 6, 1, 12, tzinfo=UTC))
    assert todo.duration == timedelta(hours=1)


def test_due_wins_over_created_and_completed():
    """The ``DUE`` row of the table has wildcards for ``COMPLETED`` and ``CREATED``.

    So ``DUE`` alone decides, even when both of the others are present.
    """
    todo = Todo()
    todo.end = datetime(2026, 1, 1, 12, tzinfo=UTC)
    todo.add("CREATED", datetime(2025, 1, 1, 10, tzinfo=UTC))
    todo.add("COMPLETED", datetime(2026, 6, 1, 12, tzinfo=UTC))
    assert todo.duration == timedelta(0)


# ---------------------------------------------------------------------------
# Undecided: the indefinite rows of the table.
#
# RFC 4791 says a task with only CREATED, or with none of these properties at
# all, matches an open-ended time range - an indefinite duration.  timedelta
# has no infinity, so this test only pins down today's behaviour; issue #496
# asks whether raising is the right answer.  The empty-task case is already
# tested in test_issue_867_todo_duration_fix.py.
# ---------------------------------------------------------------------------


def test_created_alone_is_indefinite():
    """A task with only ``CREATED`` has no computable duration."""
    todo = Todo()
    todo.add("CREATED", datetime(2026, 1, 1, 12, tzinfo=UTC))
    with pytest.raises(IncompleteComponent):
        todo.duration
