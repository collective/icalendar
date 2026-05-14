""":rfc:`5545` iCalendar component."""

from __future__ import annotations

import uuid
from datetime import timedelta
from typing import TYPE_CHECKING, Literal, cast, overload

from icalendar.attr import (
    CONCEPTS_TYPE_SETTER,
    LINKS_TYPE_SETTER,
    RELATED_TO_TYPE_SETTER,
    categories_property,
    images_property,
    multi_language_text_property,
    single_string_property,
    source_property,
    uid_property,
    url_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example
from icalendar.cal.timezone import Timezone
from icalendar.error import IncompleteComponent
from icalendar.parser.ical.calendar import CalendarIcalParser
from icalendar.version import __version__

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from datetime import date, datetime
    from pathlib import Path

    from icalendar.cal.availability import Availability
    from icalendar.cal.event import Event
    from icalendar.cal.free_busy import FreeBusy
    from icalendar.cal.journal import Journal
    from icalendar.cal.todo import Todo
    from icalendar.parser.ical.component import ComponentIcalParser


DEFAULT_PRODID = f"-//collective//icalendar//{__version__}//EN"


class Calendar(Component):
    """
        The "VCALENDAR" object is a collection of calendar information.
        This information can include a variety of components, such as
        "VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY", "VTIMEZONE", or any
        other type of calendar component.

    Examples:
        Create a new Calendar:

            >>> from icalendar import Calendar
            >>> calendar = Calendar.new(name="My Calendar")
            >>> print(calendar.calendar_name)
            My Calendar

    """

    name = "VCALENDAR"
    canonical_order = (
        "VERSION",
        "PRODID",
        "CALSCALE",
        "METHOD",
        "DESCRIPTION",
        "X-WR-CALDESC",
        "NAME",
        "X-WR-CALNAME",
    )
    required = (
        "PRODID",
        "VERSION",
    )
    singletons = (
        "PRODID",
        "VERSION",
        "CALSCALE",
        "METHOD",
        "COLOR",  # RFC 7986
    )
    multiple = (
        "CATEGORIES",  # RFC 7986
        "DESCRIPTION",  # RFC 7986
        "NAME",  # RFC 7986
    )

    @classmethod
    def example(cls, name: str = "example") -> Calendar:
        """Return the calendar example with the given name."""
        return cls.from_ical(get_example("calendars", name))

    @classmethod
    def _get_ical_parser(cls, st: str | bytes) -> ComponentIcalParser:
        """Get the iCal parser for the given input string."""
        return CalendarIcalParser(st, cls._get_component_factory(), cls.types_factory)

    @overload
    @classmethod
    def from_ical(
        cls, st: str | bytes | Path, multiple: Literal[False] = False
    ) -> Calendar: ...

    @overload
    @classmethod
    def from_ical(
        cls, st: str | bytes | Path, multiple: Literal[True]
    ) -> list[Calendar]: ...

    @classmethod
    def from_ical(
        cls, st: str | bytes | Path, multiple: bool = False
    ) -> Calendar | list[Calendar]:
        """Parse iCalendar data into calendar instances.

        Parameters:
            st: iCalendar data as bytes or string, or a path to an iCalendar file.
            multiple: If ``True``, returns a list of calendars.
                If ``False``, returns a single calendar.

        Returns:
            Calendar or list of calendars.
        """
        return cast(
            "Calendar | list[Calendar]", super().from_ical(st, multiple=multiple)
        )

    @property
    def events(self) -> list[Event]:
        """All event components in the calendar.

        This is a shortcut to get all events.
        Modifications do not change the calendar.
        Use :meth:`Component.add_component <icalendar.cal.component.Component.add_component>`.

        >>> from icalendar import Calendar
        >>> calendar = Calendar.example()
        >>> event = calendar.events[0]
        >>> event.start
        datetime.date(2022, 1, 1)
        >>> print(event["SUMMARY"])
        New Year's Day
        """
        return self.walk("VEVENT")

    @property
    def todos(self) -> list[Todo]:
        """All todo components in the calendar.

        This is a shortcut to get all todos.
        Modifications do not change the calendar.
        Use :meth:`Component.add_component <icalendar.cal.component.Component.add_component>`.
        """
        return self.walk("VTODO")

    @property
    def journals(self) -> list[Journal]:
        """All journal components in the calendar.

        This is a shortcut to get all journals.
        Modifications do not change the calendar.
        Use :meth:`Component.add_component <icalendar.cal.component.Component.add_component>`.
        """
        return self.walk("VJOURNAL")

    @property
    def availabilities(self) -> list[Availability]:
        """All :class:`Availability` components in the calendar.

        This is a shortcut to get all availabilities.
        Modifications do not change the calendar.
        Use :meth:`Component.add_component <icalendar.cal.component.Component.add_component>`.
        """
        return self.walk("VAVAILABILITY")

    @property
    def freebusy(self) -> list[FreeBusy]:
        """All FreeBusy components in the calendar.

        This is a shortcut to get all FreeBusy.
        Modifications do not change the calendar.
        Use :meth:`Component.add_component <icalendar.cal.component.Component.add_component>`.
        """
        return self.walk("VFREEBUSY")

    def get_used_tzids(self) -> set[str]:
        """The set of TZIDs in use.

        This goes through the whole calendar to find all occurrences of
        timezone information like the TZID parameter in all attributes.

        >>> from icalendar import Calendar
        >>> calendar = Calendar.example("timezone_rdate")
        >>> calendar.get_used_tzids()
        {'posix/Europe/Vaduz'}

        Even if you use UTC, this will not show up.
        """
        result = set()
        for _name, value in self.property_items(sorted=False):
            if hasattr(value, "params"):
                result.add(value.params.get("TZID"))
        return result - {None}

    def get_missing_tzids(self) -> set[str]:
        """The set of missing timezone component tzids.

        To create a :rfc:`5545` compatible calendar,
        all of these timezones should be added.

        UTC is excluded: per :rfc:`5545#section-3.2.19`, UTC datetimes use
        the ``Z`` suffix and never require a VTIMEZONE component.
        """
        tzids = self.get_used_tzids() - {"UTC"}
        for timezone in self.timezones:
            # discard (not remove) — a VTIMEZONE may exist for a timezone not
            # referenced by any event TZID (e.g. added by x-wr-timezone conversion)
            tzids.discard(timezone.tz_name)
        return tzids

    @property
    def timezones(self) -> list[Timezone]:
        """Return the timezones components in this calendar.

        >>> from icalendar import Calendar
        >>> calendar = Calendar.example("pacific_fiji")
        >>> [timezone.tz_name for timezone in calendar.timezones]
        ['custom_Pacific/Fiji']

        .. note::

            This is a read-only property.
        """
        return self.walk("VTIMEZONE")

    def add_missing_timezones(
        self,
        first_date: date = Timezone.DEFAULT_FIRST_DATE,
        last_date: date = Timezone.DEFAULT_LAST_DATE,
    ):
        """Add all missing VTIMEZONE components.

        This adds all the timezone components that are required.
        VTIMEZONE components are inserted at the beginning of the calendar
        to ensure they appear before other components that reference them.

        .. note::

            Timezones that are not known will not be added.

        Parameters:
            first_date: Earlier than anything that happens in the calendar.
            last_date: Later than anything happening in the calendar.

        >>> from icalendar import Calendar, Event
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> calendar = Calendar()
        >>> event = Event()
        >>> calendar.add_component(event)
        >>> event.start = datetime(1990, 10, 11, 12, tzinfo=ZoneInfo("Europe/Berlin"))
        >>> calendar.timezones
        []
        >>> calendar.add_missing_timezones()
        >>> calendar.timezones[0].tz_name
        'Europe/Berlin'
        >>> calendar.get_missing_tzids()  # check that all are added
        set()
        """
        missing_tzids = self.get_missing_tzids()
        if not missing_tzids:
            return

        existing_timezone_count = len(self.timezones)

        for tzid in missing_tzids:
            try:
                timezone = Timezone.from_tzid(
                    tzid, first_date=first_date, last_date=last_date
                )
            except ValueError:
                continue
            self.subcomponents.insert(existing_timezone_count, timezone)
            existing_timezone_count += 1

    calendar_name = multi_language_text_property(
        "NAME",
        "X-WR-CALNAME",
        """The display name of this calendar, per :rfc:`7986#section-5.3`.

    Implements both the ``NAME`` property (from :rfc:`7986`) and the widely-used
    ``X-WR-CALNAME`` extension for broader client compatibility.

    Multiple language variants can be stored by setting this property more than
    once, each with a different ``LANGUAGE`` parameter value.

    Example:
        Set the name of the calendar.

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.calendar_name = "My Calendar"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            NAME:My Calendar
            X-WR-CALNAME:My Calendar
            END:VCALENDAR

    See also:
        :attr:`description`
    """,
    )

    description = multi_language_text_property(
        "DESCRIPTION",
        "X-WR-CALDESC",
        """A human-readable description of this calendar's content, per :rfc:`7986#section-5.2`.

    Implements both ``DESCRIPTION`` (from :rfc:`7986`) and ``X-WR-CALDESC``
    for broader calendar client compatibility.

    Multiple language variants can be stored by setting this property more than
    once with different ``LANGUAGE`` parameter values.

    Example:
        Add a description to a calendar.

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.description = "This is a calendar"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            DESCRIPTION:This is a calendar
            X-WR-CALDESC:This is a calendar
            END:VCALENDAR

    See also:
        :attr:`calendar_name`
    """,
    )

    color = single_string_property(
        "COLOR",
        """A CSS3 color name or value used to visually distinguish this calendar, per :rfc:`7986#section-5.9`.

    Implements both ``COLOR`` (from :rfc:`7986`) and ``X-APPLE-CALENDAR-COLOR``.
    The value is a case-insensitive CSS3 color name (e.g. ``"turquoise"``) or
    a hex code (e.g. ``"#ffffff"``), drawn from the
    `CSS3 color specification <https://www.w3.org/TR/css-color-3/>`_.

    Since :rfc:`7986`, individual ``VEVENT``, ``VTODO``, and ``VJOURNAL``
    subcomponents may also carry their own color.

    Example:
        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.color = "black"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            COLOR:black
            END:VCALENDAR

    See also:
        :attr:`calendar_name`
    """,
        "X-APPLE-CALENDAR-COLOR",
    )
    categories = categories_property
    uid = uid_property
    prodid = single_string_property(
        "PRODID",
        """The product identifier for the software that created this iCalendar object.

Defined in :rfc:`5545#section-3.7.3` and required exactly once per calendar object.

The value should be a globally unique string. The conventional format is a
Formal Public Identifier (FPI), e.g. ``-//My Company//My Product//EN``, but any
unique string is acceptable.

Example:
    Set a custom product identifier on a new calendar.

    .. code-block:: pycon

        >>> from icalendar import Calendar
        >>> cal = Calendar()
        >>> cal.prodid = "-//MyApp//MyCalendar//EN"
        >>> cal.prodid
        '-//MyApp//MyCalendar//EN'

See also:
    :attr:`version`
""",
    )
    version = single_string_property(
        "VERSION",
        """The iCalendar specification version required to interpret this object.

Defined in :rfc:`5545#section-3.7.4` and required exactly once per calendar object.
The value ``"2.0"`` indicates :rfc:`5545` compliance, which is the default used
by this library. A range such as ``"1.0;2.0"`` may indicate minimum and maximum
supported versions.

Example:
    .. code-block:: pycon

        >>> from icalendar import Calendar
        >>> cal = Calendar()
        >>> cal.version = "2.0"
        >>> cal.version
        '2.0'

See also:
    :attr:`prodid`, :attr:`calscale`
""",
    )

    calscale = single_string_property(
        "CALSCALE",
        """The calendar scale for date and time values in this iCalendar object.

Defined in :rfc:`5545#section-3.7.1`. The only value currently defined is
``"GREGORIAN"`` (the default). When this property is absent, Gregorian is assumed.

Per :rfc:`7529`, non-Gregorian calendar systems are expressed via ``RRULE``
transformations rather than a different ``CALSCALE`` value.

Example:
    .. code-block:: pycon

        >>> from icalendar import Calendar
        >>> cal = Calendar()
        >>> cal.calscale
        'GREGORIAN'

See also:
    :attr:`version`
        """,
        default="GREGORIAN",
    )
    method = single_string_property(
        "METHOD",
        """The iTIP scheduling method associated with this calendar object, per :rfc:`5545#section-3.7.2`.

When present, ``METHOD`` indicates that this object is part of a scheduling
transaction (e.g., a meeting invitation or cancellation). Scheduling methods
are defined by :rfc:`5546` (iTIP), with values such as ``"REQUEST"``,
``"REPLY"``, ``"CANCEL"``, and ``"PUBLISH"``.

When used inside a MIME message, this value must match the ``method`` parameter
of the ``Content-Type`` header. If absent, the calendar is treated as a plain
data snapshot with no scheduling semantics.

Example:
    .. code-block:: pycon

        >>> from icalendar import Calendar
        >>> cal = Calendar()
        >>> cal.method = "REQUEST"
        >>> cal.method
        'REQUEST'

See also:
    :attr:`version`, :rfc:`5546`
""",
    )
    url = url_property
    source = source_property

    @property
    def refresh_interval(self) -> timedelta | None:
        """A suggested minimum polling interval for fetching updates to this calendar, per :rfc:`7986#section-5.7`.

        Returns a :class:`~datetime.timedelta` or ``None`` when not set.
        Calendar clients should not poll more frequently than this interval.
        The value must be a positive duration.

        Raises:
            ValueError: When setting a non-positive (zero or negative) duration.
            TypeError: When setting a value that is not a :class:`~datetime.timedelta` or ``None``.

        Example:
            .. code-block:: pycon

                >>> from datetime import timedelta
                >>> from icalendar import Calendar
                >>> cal = Calendar()
                >>> cal.refresh_interval = timedelta(hours=1)
                >>> cal.refresh_interval
                datetime.timedelta(seconds=3600)

        See also:
            :attr:`source`
        """
        refresh_interval = self.get("REFRESH-INTERVAL")
        return refresh_interval.dt if refresh_interval else None

    @refresh_interval.setter
    def refresh_interval(self, value: timedelta | None):
        """Set the REFRESH-INTERVAL."""
        if not isinstance(value, timedelta) and value is not None:
            raise TypeError(
                "REFRESH-INTERVAL must be either a positive timedelta,"
                " or None to delete it."
            )
        if value is not None and value.total_seconds() <= 0:
            raise ValueError("REFRESH-INTERVAL must be a positive timedelta.")
        if value is not None:
            del self.refresh_interval
            self.add("REFRESH-INTERVAL", value)
        else:
            del self.refresh_interval

    @refresh_interval.deleter
    def refresh_interval(self):
        """Delete REFRESH-INTERVAL."""
        self.pop("REFRESH-INTERVAL")

    images = images_property

    @classmethod
    def new(
        cls,
        /,
        calscale: str | None = None,
        categories: Sequence[str] = (),
        color: str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
        description: str | None = None,
        language: str | None = None,
        last_modified: date | datetime | None = None,
        links: LINKS_TYPE_SETTER = None,
        method: str | None = None,
        name: str | None = None,
        organization: str | None = None,
        prodid: str | None = None,
        refresh_interval: timedelta | None = None,
        refids: list[str] | str | None = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        source: str | None = None,
        subcomponents: Iterable[Component] | None = None,
        uid: str | uuid.UUID | None = None,
        url: str | None = None,
        version: str = "2.0",
    ):
        """Create a new Calendar.

        This creates a new Calendar in accordance with :rfc:`5545` and :rfc:`7986`.

        Parameters:
            calscale: The :attr:`calscale` of the calendar.
            categories: The :attr:`categories` of the calendar.
            color: The :attr:`color` of the calendar.
            concepts: The :attr:`~icalendar.cal.component.Component.concepts` of the calendar.
            description: The :attr:`description` of the calendar.
            language: The language for the calendar. Used to generate localized `prodid`.
            last_modified: The :attr:`~icalendar.cal.component.Component.last_modified` of the calendar.
            links: The :attr:`~icalendar.cal.component.Component.links` of the calendar.
            method: The :attr:`method` of the calendar.
            name: The :attr:`calendar_name` of the calendar.
            organization: The organization name. Used to generate `prodid` if not provided.
            prodid: The :attr:`prodid` of the component. If ``None`` and ``organization`` is provided,
                generates a `prodid` in the format of "-//organization//name//language".
                If ``None`` and ``organization`` is not provided, sets it to
                :attr:`~icalendar.cal.calendar.DEFAULT_PRODID`.
            refresh_interval: The :attr:`refresh_interval` of the calendar.
            refids: :attr:`~icalendar.cal.component.Component.refids` of the calendar.
            related_to: :attr:`~icalendar.cal.component.Component.related_to` of the calendar.
            source: The :attr:`source` of the calendar.
            subcomponents: The subcomponents of the calendar.
            uid: The :attr:`uid` of the calendar.
                If None, this is set to a new :func:`uuid.uuid4`.
            url: The :attr:`url` of the calendar.
            version: The :attr:`version` of the calendar.

        Returns:
            :class:`Calendar`

        Raises:
            ~error.InvalidCalendar: If the content is not valid according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        calendar: Calendar = super().new(
            last_modified=last_modified,
            links=links,
            related_to=related_to,
            refids=refids,
            concepts=concepts,
            subcomponents=subcomponents,
        )

        # Generate prodid if not provided but organization is given
        if prodid is None and organization:
            app_name = name or "Calendar"
            lang = language.upper() if language else "EN"
            prodid = f"-//{organization}//{app_name}//{lang}"
        elif prodid is None:
            prodid = DEFAULT_PRODID

        calendar.prodid = prodid
        calendar.version = version
        calendar.calendar_name = name
        calendar.color = color
        calendar.description = description
        calendar.method = method
        calendar.calscale = calscale
        calendar.categories = categories
        calendar.uid = uid if uid is not None else uuid.uuid4()
        calendar.url = url
        calendar.refresh_interval = refresh_interval
        calendar.source = source

        return calendar

    def validate(self):
        """Validate that the calendar has required properties and components.

        This method can be called explicitly to validate a calendar before output.

        Raises:
            ~error.IncompleteComponent: If the calendar lacks required properties or
                components.
        """
        if not self.get("PRODID"):
            raise IncompleteComponent("Calendar must have a PRODID")
        if not self.get("VERSION"):
            raise IncompleteComponent("Calendar must have a VERSION")
        if not self.subcomponents:
            raise IncompleteComponent(
                "Calendar must contain at least one component (event, todo, etc.)"
            )


__all__ = ["Calendar"]
