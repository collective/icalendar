""":rfc:`5545` VALARM component."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, NamedTuple

from icalendar.attr import (
    CONCEPTS_TYPE_SETTER,
    LINKS_TYPE_SETTER,
    RELATED_TO_TYPE_SETTER,
    attendees_property,
    create_single_property,
    description_property,
    property_del_duration,
    property_get_duration,
    property_set_duration,
    repeat_property,
    single_int_property,
    single_string_property,
    single_utc_property,
    summary_property,
    uid_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example
from icalendar.error import InvalidCalendar
from icalendar.prop.binary import vBinary

if TYPE_CHECKING:
    import uuid
    from collections.abc import Sequence

    from icalendar.compatibility import Self
    from icalendar.prop import vCalAddress


class Alarm(Component):
    """
    A "VALARM" calendar component is a grouping of component
    properties that defines an alarm or reminder for an event or a
    to-do. For example, it may be used to define a reminder for a
    pending event or an overdue to-do.

    Example:

        The following example creates an alarm which uses an audio file
        from an FTP server.

        .. code-block:: pycon

            >>> from icalendar import Alarm
            >>> alarm = Alarm.example()
            >>> print(alarm.to_ical().decode())
            BEGIN:VALARM
            ACTION:AUDIO
            ATTACH;FMTTYPE=audio/basic:ftp://example.com/pub/sounds/bell-01.aud
            DURATION:PT15M
            REPEAT:4
            TRIGGER;VALUE=DATE-TIME:19970317T133000Z
            END:VALARM
    """

    name = "VALARM"
    # some properties MAY/MUST/MUST NOT appear depending on ACTION value
    required = (
        "ACTION",
        "TRIGGER",
    )
    singletons = (
        "ACTION",
        "DESCRIPTION",
        "SUMMARY",
        "TRIGGER",
        "DURATION",
        "REPEAT",
        "UID",
        "PROXIMITY",
        "ACKNOWLEDGED",
    )
    inclusive = (
        (
            "DURATION",
            "REPEAT",
        ),
        (
            "SUMMARY",
            "ATTENDEE",
        ),
    )
    multiple = ("ATTENDEE", "ATTACH", "RELATED-TO")

    REPEAT = single_int_property(
        "REPEAT",
        0,
        """The number of additional times the alarm is triggered after the initial trigger.

        Defaults to ``0``, meaning the alarm fires once. To repeat the alarm,
        set both :attr:`REPEAT` and :attr:`DURATION`. The :attr:`DURATION`
        sets the gap between repetitions. :attr:`REPEAT` is the count of *additional*
        triggers, so a :attr:`REPEAT` of ``2`` produces three alarms in total
        (the initial trigger plus two repeats).

        Conforming with :rfc:`5545#section-3.8.6.2`, this property can appear
        once in an :class:`~icalendar.cal.alarm.Alarm` component and must be
        paired with :attr:`DURATION`.

        Example:
            Build an alarm that fires once and then repeats twice at
            five-minute intervals.

            .. code-block:: pycon

                >>> from datetime import timedelta
                >>> from icalendar import Alarm
                >>> alarm = Alarm()
                >>> alarm.TRIGGER = timedelta(minutes=-15)
                >>> alarm.DURATION = timedelta(minutes=5)
                >>> alarm.REPEAT = 2
                >>> alarm.REPEAT
                2

        Raises:
            TypeError: If the value is not an ``int``. Booleans are rejected, too,
                even though ``bool`` subclasses ``int``.

            ~icalendar.error.InvalidCalendar: If the value is negative.

        ..  versionchanged:: 7.2.3
            Negative values are no longer accepted.
        """,
        min_value=0,
    )

    DURATION = property(
        property_get_duration,
        property_set_duration,
        property_del_duration,
        """The delay between repeated triggers of a repeating alarm.

        Returns a :class:`datetime.timedelta` or ``None`` when the alarm
        has no :attr:`DURATION` set. Setting this attribute accepts a
        :class:`~datetime.timedelta`; deleting it removes the property
        from the component.

        :attr:`DURATION` is meaningful only for repeating alarms and must
        be paired with :attr:`REPEAT`. The two together produce
        :attr:`REPEAT` additional triggers, each spaced by :attr:`DURATION` after
        the initial trigger.

        Conforming with :rfc:`5545#section-3.8.2.5`, the :attr:`DURATION` property
        can appear once in an :class:`~icalendar.cal.alarm.Alarm` component.

        Example:
            Pair :attr:`DURATION` with :attr:`REPEAT` to produce three
            triggers spaced ten minutes apart.

            .. code-block:: pycon

                >>> from datetime import timedelta
                >>> from icalendar import Alarm
                >>> alarm = Alarm()
                >>> alarm.TRIGGER = timedelta(minutes=-30)
                >>> alarm.DURATION = timedelta(minutes=10)
                >>> alarm.REPEAT = 2
                >>> alarm.DURATION
                datetime.timedelta(seconds=600)
        """,
    )

    ACKNOWLEDGED = single_utc_property(
        "ACKNOWLEDGED",
        """This property is the UTC datetime at which this alarm was last sent or acknowledged as defined in :rfc:`9074`.

    Setting this property allows calendar clients to
    dismiss or suppress an alarm across multiple devices. Once set to a value
    greater than or equal to the alarm's computed trigger time, conforming clients
    will not refire the alarm.

    Returns ``None`` when no acknowledgment has been recorded.

    Example:
        Mark an alarm as acknowledged. Note that the example uses an arbitrary time
        for the purpose of passing doctests. In actual practice, clients should
        use the current time in UTC, such as ``datetime.now(UTC)``.

        .. code-block:: pycon

            >>> from datetime import timezone, datetime
            >>> from icalendar import Alarm
            >>> UTC = timezone.utc
            >>> alarm = Alarm()
            >>> alarm.ACKNOWLEDGED = datetime(2024, 1, 15, 10, 0, tzinfo=UTC)
            >>> alarm.ACKNOWLEDGED
            datetime.datetime(2024, 1, 15, 10, 0, tzinfo=ZoneInfo(key='UTC'))

    See also:
        :attr:`TRIGGER`, the time at which the alarm fires.
    """,
    )

    TRIGGER = create_single_property(
        "TRIGGER",
        "dt",
        (datetime, timedelta),
        timedelta | datetime | None,
        """The time at which this alarm fires, per :rfc:`5545#section-3.8.6.3`.

    The value is either a :class:`~datetime.timedelta` (relative trigger) or a
    UTC :class:`~datetime.datetime` (absolute trigger).

    A negative :class:`~datetime.timedelta` fires *before* the related
    component boundary (start or end); a positive one fires *after* it.
    Use :attr:`TRIGGER_RELATED` to choose whether the offset is measured from
    the start or the end of the parent event or to-do.
    An absolute trigger fires at an exact UTC point in time regardless of the
    parent component's dates.

    Examples:
        Set an alarm to fire 15 minutes before the start of an event.

        .. code-block:: pycon

            >>> from datetime import datetime, timedelta, timezone
            >>> from icalendar import Alarm, Event
            >>> UTC = timezone.utc
            >>> event = Event()
            >>> event.start = datetime(2024, 1, 15, 10, 0, tzinfo=UTC)
            >>> alarm = Alarm()
            >>> alarm.TRIGGER = timedelta(minutes=-15)
            >>> event.add_component(alarm)
            >>> event.alarms.times[0].trigger
            datetime.datetime(2024, 1, 15, 9, 45, tzinfo=datetime.timezone.utc)

        Set an absolute trigger to fire at a specific UTC time.

        .. code-block:: pycon

            >>> absolute_alarm = Alarm()
            >>> absolute_alarm.TRIGGER = datetime(2024, 1, 15, 9, 45, tzinfo=UTC)
            >>> absolute_alarm.TRIGGER
            datetime.datetime(2024, 1, 15, 9, 45, tzinfo=datetime.timezone.utc)

    See also:
        :attr:`TRIGGER_RELATED`, :attr:`DURATION`, :attr:`REPEAT`
    """,
    )

    @property
    def TRIGGER_RELATED(self) -> str:
        """The RELATED parameter of the TRIGGER property.

        Values are either "START" (default) or "END".

        A value of START will set the alarm to trigger off the
        start of the associated event or to-do.  A value of END will set
        the alarm to trigger off the end of the associated event or to-do.

        In this example, we create an alarm that triggers two hours after the
        end of its parent component.

        >>> from icalendar import Alarm
        >>> from datetime import timedelta
        >>> alarm = Alarm()
        >>> alarm.TRIGGER = timedelta(hours=2)
        >>> alarm.TRIGGER_RELATED = "END"
        """
        trigger = self.get("TRIGGER")
        if trigger is None:
            return "START"
        return trigger.params.get("RELATED", "START")

    @TRIGGER_RELATED.setter
    def TRIGGER_RELATED(self, value: str):
        """Set "START" or "END"."""
        trigger = self.get("TRIGGER")
        if trigger is None:
            raise ValueError(
                "You must set a TRIGGER before setting the RELATED parameter."
            )
        trigger.params["RELATED"] = value

    class Triggers(NamedTuple):
        """The computed times of alarm triggers.

        start - triggers relative to the start of the Event or Todo (timedelta)

        end - triggers relative to the end of the Event or Todo (timedelta)

        absolute - triggers at a datetime in UTC
        """

        start: tuple[timedelta]
        end: tuple[timedelta]
        absolute: tuple[datetime]

    @property
    def triggers(self):
        """The computed triggers of an Alarm.

        This takes the TRIGGER, DURATION and REPEAT properties into account.

        Here, we create an alarm that triggers 3 times before the start of the
        parent component.

        >>> from icalendar import Alarm
        >>> from datetime import timedelta
        >>> alarm = Alarm()
        >>> alarm.TRIGGER = timedelta(hours=-4)  # trigger 4 hours before START
        >>> alarm.DURATION = timedelta(hours=1)  # after 1 hour trigger again
        >>> alarm.REPEAT = 2  # trigger 2 more times
        >>> alarm.triggers.start == (timedelta(hours=-4),  timedelta(hours=-3),  timedelta(hours=-2))
        True
        >>> alarm.triggers.end
        ()
        >>> alarm.triggers.absolute
        ()
        """
        start = []
        end = []
        absolute = []
        trigger = self.TRIGGER
        if trigger is not None:
            if isinstance(trigger, date):
                absolute.append(trigger)
                add = absolute
            elif self.TRIGGER_RELATED == "START":
                start.append(trigger)
                add = start
            else:
                end.append(trigger)
                add = end
            duration = self.DURATION
            if duration is not None:
                for _ in range(self.repeat):
                    add.append(add[-1] + duration)
        return self.Triggers(
            start=tuple(start), end=tuple(end), absolute=tuple(absolute)
        )

    repeat = repeat_property

    ACTION = single_string_property(
        "ACTION",
        """The action invoked when the alarm triggers.

        Typical values defined by :rfc:`5545#section-3.8.6.1` are
        ``AUDIO``, ``DISPLAY``, and ``EMAIL``. The empty string is
        returned when no ``ACTION`` property is present.
        """,
    )
    uid = single_string_property(
        "UID",
        uid_property.__doc__,
        ["X-ALARMUID", "X-EVOLUTION-ALARM-UID"],
    )
    summary = summary_property
    description = description_property
    attendees = attendees_property

    @classmethod
    def new(
        cls,
        /,
        attendees: list[vCalAddress] | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
        description: str | None = None,
        links: LINKS_TYPE_SETTER = None,
        refids: list[str] | str | None = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        summary: str | None = None,
        uid: str | uuid.UUID | None = None,
    ) -> Self:
        """Create a new alarm with all required properties.

        This creates a new Alarm in accordance with :rfc:`5545`.

        Parameters:
            attendees: The :attr:`attendees` of the alarm.
            concepts: The :attr:`~icalendar.cal.component.Component.concepts` of the alarm.
            description: The :attr:`description` of the alarm.
            links: The :attr:`~icalendar.cal.component.Component.links` of the alarm.
            refids: :attr:`~icalendar.cal.component.Component.refids` of the alarm.
            related_to: :attr:`~icalendar.cal.component.Component.related_to` of the alarm.
            summary: The :attr:`summary` of the alarm.
            uid: The :attr:`uid` of the alarm.

        Returns:
            :class:`Alarm`

        Raises:
            ~error.InvalidCalendar: If the content is not valid
                according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        alarm: Self = super().new(
            links=links,
            related_to=related_to,
            refids=refids,
            concepts=concepts,
        )
        alarm.summary = summary
        alarm.description = description
        alarm.uid = uid
        alarm.attendees = attendees
        return alarm

    def _apply_duration_repeat(
        self,
        duration: timedelta | None,
        repeat: int | None,
    ) -> None:
        if duration is not None or repeat is not None:
            if duration is None or repeat is None:
                raise InvalidCalendar(
                    "DURATION and REPEAT must be set together or not at all"
                )
            self.DURATION = duration
            self.REPEAT = repeat

    @classmethod
    def new_display(
        cls,
        description: str,
        trigger: timedelta | datetime,
        duration: timedelta | None = None,
        repeat: int | None = None,
        uid: str | uuid.UUID | None = None,
        links: LINKS_TYPE_SETTER = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        refids: list[str] | str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
    ) -> Alarm:
        """Create a new DISPLAY alarm that shows a text reminder.

        A DISPLAY alarm pops up a text notification at the trigger time.
        This is the most common alarm type used by calendar clients.

        Conforms to :rfc:`5545#section-3.6.6`.

        Parameters:
            description: Required. The text to display when the alarm fires.
                Corresponds to the :attr:`description` property.
            trigger: Required. When the alarm fires, as a :class:`~datetime.timedelta`
                relative to the event start (negative means before) or as an
                absolute :class:`~datetime.datetime` (recommend UTC-aware).
            concepts: The :attr:`~icalendar.cal.component.Component.concepts` of the alarm.
            duration: Gap between repeated triggers. Must be paired with
                ``repeat``. Corresponds to the :attr:`DURATION` property.
            links: The :attr:`~icalendar.cal.component.Component.links` of the alarm.
            refids: The :attr:`~icalendar.cal.component.Component.refids` of the alarm.
            related_to: The :attr:`~icalendar.cal.component.Component.related_to` of the alarm.
            repeat: Number of *additional* times to fire after the initial
                trigger. Must be paired with ``duration``.
                Corresponds to the :attr:`REPEAT` property.
            uid: Unique identifier for the alarm or ``None``.

        Returns:
            :class:`Alarm` with ``ACTION:DISPLAY`` set.

        Raises:
            ~icalendar.error.InvalidCalendar: If required fields are missing
                or ``duration`` and ``repeat`` are not both provided together.

        Example:
            Create a display alarm that fires 15 minutes before the event:

            .. code-block:: pycon

                >>> from datetime import timedelta
                >>> from icalendar import Alarm
                >>> alarm = Alarm.new_display(
                ...     description="Team meeting in 15 minutes",
                ...     trigger=timedelta(minutes=-15),
                ... )
                >>> print(alarm.to_ical().decode())
                BEGIN:VALARM
                ACTION:DISPLAY
                DESCRIPTION:Team meeting in 15 minutes
                TRIGGER:-PT15M
                END:VALARM

            Attach the alarm to an event:

            .. code-block:: python

                from datetime import datetime, timedelta, timezone
                from icalendar import Alarm, Event

                event = Event.new(
                    summary="Team meeting",
                    start=datetime(2025, 6, 1, 10, 0, tzinfo=timezone.utc),
                    end=datetime(2025, 6, 1, 11, 0, tzinfo=timezone.utc),
                )
                event.add_component(Alarm.new_display(
                    description="Team meeting in 15 minutes",
                    trigger=timedelta(minutes=-15),
                ))
        """
        if not description:
            raise InvalidCalendar("DISPLAY alarm requires a description")
        if trigger is None:
            raise InvalidCalendar("DISPLAY alarm requires a trigger")
        alarm: Alarm = cls.new(
            description=description,
            uid=uid,
            links=links,
            related_to=related_to,
            refids=refids,
            concepts=concepts,
        )
        alarm.add("ACTION", "DISPLAY")
        alarm.TRIGGER = trigger
        alarm._apply_duration_repeat(duration, repeat)
        return alarm

    @classmethod
    def new_audio(
        cls,
        trigger: timedelta | datetime,
        attach: str | bytes | None = None,
        duration: timedelta | None = None,
        repeat: int | None = None,
        uid: str | uuid.UUID | None = None,
        links: LINKS_TYPE_SETTER = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        refids: list[str] | str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
    ) -> Alarm:
        """Create a new AUDIO alarm that plays a sound.

        An AUDIO alarm plays a sound at the trigger time. An optional
        ``attach`` URI points to the audio file to play; when omitted,
        the client uses its default alert sound.

        Conforms to :rfc:`5545#section-3.6.6`.

        Parameters:
            trigger: Required. When the alarm fires, as a :class:`~datetime.timedelta`
                relative to the event start (negative means before) or as an
                absolute :class:`~datetime.datetime` (recommend UTC-aware).
            attach: Optional audio attachment. Pass a URI string such as
                ``"ftp://example.com/pub/sounds/bell.aud"`` for a linked
                sound file, or :class:`bytes` for inline binary audio data
                (stored as ``VALUE=BINARY``). When ``None`` the client uses
                its default sound.
            concepts: The :attr:`~icalendar.cal.component.Component.concepts` of the alarm.
            duration: Gap between repeated triggers. Must be paired with
                ``repeat``. Corresponds to the :attr:`DURATION` property.
            links: The :attr:`~icalendar.cal.component.Component.links` of the alarm.
            refids: The :attr:`~icalendar.cal.component.Component.refids` of the alarm.
            related_to: The :attr:`~icalendar.cal.component.Component.related_to` of the alarm.
            repeat: Number of *additional* times to fire after the initial
                trigger. Must be paired with ``duration``.
                Corresponds to the :attr:`REPEAT` property.
            uid: Unique identifier for the alarm or ``None``.

        Returns:
            :class:`Alarm` with ``ACTION:AUDIO`` set.

        Raises:
            ~icalendar.error.InvalidCalendar: If required fields are missing
                or ``duration`` and ``repeat`` are not both provided together.

        Example:
            Create an audio alarm using a custom sound file:

            .. code-block:: pycon

                >>> from datetime import timedelta
                >>> from icalendar import Alarm
                >>> alarm = Alarm.new_audio(
                ...     trigger=timedelta(minutes=-5),
                ...     attach="ftp://example.com/pub/sounds/bell-01.aud",
                ... )
                >>> print(alarm.to_ical().decode())
                BEGIN:VALARM
                ACTION:AUDIO
                ATTACH:ftp://example.com/pub/sounds/bell-01.aud
                TRIGGER:-PT5M
                END:VALARM
        """
        if trigger is None:
            raise InvalidCalendar("AUDIO alarm requires a trigger")
        alarm: Alarm = cls.new(
            uid=uid,
            links=links,
            related_to=related_to,
            refids=refids,
            concepts=concepts,
        )
        alarm.add("ACTION", "AUDIO")
        alarm.TRIGGER = trigger
        if attach:
            alarm.add(
                "ATTACH", vBinary(attach) if isinstance(attach, bytes) else attach
            )
        alarm._apply_duration_repeat(duration, repeat)
        return alarm

    @classmethod
    def new_email(
        cls,
        summary: str,
        description: str,
        trigger: timedelta | datetime,
        attendees: Sequence[vCalAddress] | vCalAddress,
        attachments: Sequence[str] | str | None = None,
        duration: timedelta | None = None,
        repeat: int | None = None,
        uid: str | uuid.UUID | None = None,
        links: LINKS_TYPE_SETTER = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        refids: list[str] | str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
    ) -> Alarm:
        """Create a new EMAIL alarm that sends an email notification.

        An EMAIL alarm sends an email to each address in ``attendees`` when
        the alarm fires.

        Conforms to :rfc:`5545#section-3.6.6`.

        Parameters:
            attendees: Required. One or more recipient addresses as
                :class:`~icalendar.prop.cal_address.vCalAddress` instances. A
                single address or a sequence of addresses. At least one is
                required.
            description: Required. Body of the email.
                Corresponds to the :attr:`description` property.
            summary: Required. Subject line of the email.
                Corresponds to the :attr:`summary` property.
            trigger: Required. When the alarm fires, as a :class:`~datetime.timedelta`
                relative to the event start (negative means before) or as an
                absolute :class:`~datetime.datetime` (recommend UTC-aware).
            attachments: Optional URI or sequence of URIs to attach to the
                email.
            concepts: The :attr:`~icalendar.cal.component.Component.concepts` of the alarm.
            duration: Gap between repeated triggers. Must be paired with
                ``repeat``. Corresponds to the :attr:`DURATION` property.
            links: The :attr:`~icalendar.cal.component.Component.links` of the alarm.
            refids: The :attr:`~icalendar.cal.component.Component.refids` of the alarm.
            related_to: The :attr:`~icalendar.cal.component.Component.related_to` of the alarm.
            repeat: Number of *additional* times to fire after the initial
                trigger. Must be paired with ``duration``.
                Corresponds to the :attr:`REPEAT` property.
            uid: Unique identifier for the alarm or ``None``.

        Returns:
            :class:`Alarm` with ``ACTION:EMAIL`` set.

        Raises:
            ~icalendar.error.InvalidCalendar: If required fields are missing,
                ``attendees`` is empty, or ``duration`` and ``repeat`` are not
                both provided together.

        Example:
            Create an email alarm sent to two recipients:

            .. code-block:: pycon

                >>> from datetime import timedelta
                >>> from icalendar import Alarm, vCalAddress
                >>> alarm = Alarm.new_email(
                ...     summary="Meeting reminder",
                ...     description="Your meeting starts in 30 minutes.",
                ...     trigger=timedelta(minutes=-30),
                ...     attendees=[vCalAddress("mailto:user@example.com")],
                ... )
                >>> print(alarm.to_ical().decode())
                BEGIN:VALARM
                ACTION:EMAIL
                ATTENDEE:mailto:user@example.com
                DESCRIPTION:Your meeting starts in 30 minutes.
                SUMMARY:Meeting reminder
                TRIGGER:-PT30M
                END:VALARM
        """
        if isinstance(attendees, str):
            attendees = [attendees]
        if isinstance(attachments, str):
            attachments = [attachments]
        if not summary:
            raise InvalidCalendar("EMAIL alarm requires a summary")
        if not description:
            raise InvalidCalendar("EMAIL alarm requires a description")
        if trigger is None:
            raise InvalidCalendar("EMAIL alarm requires a trigger")
        if not attendees:
            raise InvalidCalendar("EMAIL alarm requires at least one attendee")
        alarm: Alarm = cls.new(
            summary=summary,
            description=description,
            uid=uid,
            attendees=attendees,
            links=links,
            related_to=related_to,
            refids=refids,
            concepts=concepts,
        )
        alarm.add("ACTION", "EMAIL")
        alarm.TRIGGER = trigger
        if attachments:
            for attachment in attachments:
                alarm.add("ATTACH", attachment)
        alarm._apply_duration_repeat(duration, repeat)
        return alarm

    @classmethod
    def example(cls, name: str = "example") -> Alarm:
        """Return the alarm example with the given name."""
        return cls.from_ical(get_example("alarms", name))


__all__ = ["Alarm"]
