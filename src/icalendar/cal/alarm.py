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
    single_int_property,
    single_string_property,
    single_utc_property,
    summary_property,
    uid_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example
from icalendar.error import InvalidCalendar

if TYPE_CHECKING:
    import uuid

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
        "ATTACH",
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
        """,
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
        """This is defined in RFC 9074:

    Purpose: This property specifies the UTC date and time at which the
    corresponding alarm was last sent or acknowledged.

    This property is used to specify when an alarm was last sent or acknowledged.
    This allows clients to determine when a pending alarm has been acknowledged
    by a calendar user so that any alerts can be dismissed across multiple devices.
    It also allows clients to track repeating alarms or alarms on recurring events or
    to-dos to ensure that the right number of missed alarms can be tracked.

    Clients SHOULD set this property to the current date-time value in UTC
    when a calendar user acknowledges a pending alarm. Certain kinds of alarms,
    such as email-based alerts, might not provide feedback as to when the calendar user
    sees them. For those kinds of alarms, the client SHOULD set this property
    when the alarm is triggered and the action is successfully carried out.

    When an alarm is triggered on a client, clients can check to see if an "ACKNOWLEDGED"
    property is present. If it is, and the value of that property is greater than or
    equal to the computed trigger time for the alarm, then the client SHOULD NOT trigger
    the alarm. Similarly, if an alarm has been triggered and
    an "alert" has been presented to a calendar user, clients can monitor
    the iCalendar data to determine whether an "ACKNOWLEDGED" property is added or
    changed in the alarm component. If the value of any "ACKNOWLEDGED" property
    in the alarm changes and is greater than or equal to the trigger time of the alarm,
    then clients SHOULD dismiss or cancel any "alert" presented to the calendar user.
    """,
    )

    TRIGGER = create_single_property(
        "TRIGGER",
        "dt",
        (datetime, timedelta),
        timedelta | datetime | None,
        """Purpose:  This property specifies when an alarm will trigger.

    Value Type:  The default value type is DURATION.  The value type can
    be set to a DATE-TIME value type, in which case the value MUST
    specify a UTC-formatted DATE-TIME value.

    Either a positive or negative duration may be specified for the
    "TRIGGER" property.  An alarm with a positive duration is
    triggered after the associated start or end of the event or to-do.
    An alarm with a negative duration is triggered before the
    associated start or end of the event or to-do.""",
    )

    @property
    def TRIGGER_RELATED(self) -> str:
        """The RELATED parameter of the TRIGGER property.

        Values are either "START" (default) or "END".

        A value of START will set the alarm to trigger off the
        start of the associated event or to-do.  A value of END will set
        the alarm to trigger off the end of the associated event or to-do.

        In this example, we create an alarm that triggers two hours after the
        end of its parent component:

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
        parent component:

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
                for _ in range(self.REPEAT):
                    add.append(add[-1] + duration)
        return self.Triggers(
            start=tuple(start), end=tuple(end), absolute=tuple(absolute)
        )

    uid = single_string_property(
        "UID",
        uid_property.__doc__,
        "X-ALARMUID",
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
    ):
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
        alarm: Alarm = super().new(
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

    @classmethod
    def new_display(
        cls,
        /,
        description: str,
        trigger: timedelta | datetime,
        duration: timedelta | None = None,
        repeat: int | None = None,
        uid: str | uuid.UUID | None = None,
    ) -> Alarm:
        """Create a new DISPLAY alarm that shows a text reminder.

        A DISPLAY alarm pops up a text notification at the trigger time.
        This is the most common alarm type used by calendar clients.

        Conforms to :rfc:`5545#section-3.6.6`.

        Parameters:
            description: The text to display when the alarm fires.
                Corresponds to the :attr:`description` property.
            trigger: When the alarm fires, as a :class:`~datetime.timedelta`
                relative to the event start (negative means before) or as an
                absolute UTC :class:`~datetime.datetime`.
            duration: Gap between repeated triggers. Must be paired with
                ``repeat``. Corresponds to the :attr:`DURATION` property.
            repeat: Number of *additional* times to fire after the initial
                trigger. Must be paired with ``duration``.
                Corresponds to the :attr:`REPEAT` property.
            uid: Unique identifier for the alarm. Generated automatically
                when ``None``.

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
        """
        if not description:
            raise InvalidCalendar("DISPLAY alarm requires a description")
        if trigger is None:
            raise InvalidCalendar("DISPLAY alarm requires a trigger")
        alarm: Alarm = cls()
        alarm.add("ACTION", "DISPLAY")
        alarm.description = description
        alarm.TRIGGER = trigger
        alarm.uid = uid
        if duration is not None or repeat is not None:
            if duration is None or repeat is None:
                raise InvalidCalendar(
                    "DURATION and REPEAT must be set together or not at all"
                )
            alarm.DURATION = duration
            alarm.REPEAT = repeat
        return alarm

    @classmethod
    def new_audio(
        cls,
        /,
        trigger: timedelta | datetime,
        attach: str | None = None,
        duration: timedelta | None = None,
        repeat: int | None = None,
        uid: str | uuid.UUID | None = None,
    ) -> Alarm:
        """Create a new AUDIO alarm that plays a sound.

        An AUDIO alarm plays a sound at the trigger time. An optional
        ``attach`` URI points to the audio file to play; when omitted,
        the client uses its default alert sound.

        Conforms to :rfc:`5545#section-3.6.6`.

        Parameters:
            trigger: When the alarm fires, as a :class:`~datetime.timedelta`
                relative to the event start (negative means before) or as an
                absolute :class:`~datetime.datetime` (recommend UTC-aware).
            attach: Optional URI of the audio file to play, e.g.
                ``"ftp://example.com/pub/sounds/bell.aud"``. When ``None``
                the client uses its default sound.
            duration: Gap between repeated triggers. Must be paired with
                ``repeat``. Corresponds to the :attr:`DURATION` property.
            repeat: Number of *additional* times to fire after the initial
                trigger. Must be paired with ``duration``.
                Corresponds to the :attr:`REPEAT` property.
            uid: Unique identifier for the alarm. Generated automatically
                when ``None``.

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
        alarm: Alarm = cls()
        alarm.add("ACTION", "AUDIO")
        alarm.TRIGGER = trigger
        alarm.uid = uid
        if attach is not None:
            alarm.add("ATTACH", attach)
        if duration is not None or repeat is not None:
            if duration is None or repeat is None:
                raise InvalidCalendar(
                    "DURATION and REPEAT must be set together or not at all"
                )
            alarm.DURATION = duration
            alarm.REPEAT = repeat
        return alarm

    @classmethod
    def new_email(
        cls,
        /,
        summary: str,
        description: str,
        trigger: timedelta | datetime,
        attendees: list[vCalAddress],
        attachments: list[str] | None = None,
        duration: timedelta | None = None,
        repeat: int | None = None,
        uid: str | uuid.UUID | None = None,
    ) -> Alarm:
        """Create a new EMAIL alarm that sends an email notification.

        An EMAIL alarm sends an email to each address in ``attendees`` when
        the alarm fires.

        Conforms to :rfc:`5545#section-3.6.6`.

        Parameters:
            summary: Subject line of the email.
                Corresponds to the :attr:`summary` property.
            description: Body of the email.
                Corresponds to the :attr:`description` property.
            trigger: When the alarm fires, as a :class:`~datetime.timedelta`
                relative to the event start (negative means before) or as an
                absolute :class:`~datetime.datetime` (recommend UTC-aware).
            attendees: One or more recipient addresses as
                :class:`~icalendar.vCalAddress` instances, e.g.
                ``[vCalAddress("mailto:user@example.com")]``.
                At least one address is required.
            attachments: Optional list of URIs to attach to the email.
            duration: Gap between repeated triggers. Must be paired with
                ``repeat``. Corresponds to the :attr:`DURATION` property.
            repeat: Number of *additional* times to fire after the initial
                trigger. Must be paired with ``duration``.
                Corresponds to the :attr:`REPEAT` property.
            uid: Unique identifier for the alarm. Generated automatically
                when ``None``.

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
        if not summary:
            raise InvalidCalendar("EMAIL alarm requires a summary")
        if not description:
            raise InvalidCalendar("EMAIL alarm requires a description")
        if trigger is None:
            raise InvalidCalendar("EMAIL alarm requires a trigger")
        if not attendees:
            raise InvalidCalendar("EMAIL alarm requires at least one attendee")
        alarm: Alarm = cls()
        alarm.add("ACTION", "EMAIL")
        alarm.summary = summary
        alarm.description = description
        alarm.TRIGGER = trigger
        alarm.attendees = attendees
        alarm.uid = uid
        if attachments:
            for attachment in attachments:
                alarm.add("ATTACH", attachment)
        if duration is not None or repeat is not None:
            if duration is None or repeat is None:
                raise InvalidCalendar(
                    "DURATION and REPEAT must be set together or not at all"
                )
            alarm.DURATION = duration
            alarm.REPEAT = repeat
        return alarm

    @classmethod
    def example(cls, name: str = "example") -> Alarm:
        """Return the alarm example with the given name."""
        return cls.from_ical(get_example("alarms", name))


__all__ = ["Alarm"]
