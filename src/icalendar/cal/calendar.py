""":rfc:`5545` iCalendar component."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

from icalendar.attr import (
    categories_property,
    multi_language_text_property,
    single_string_property,
    uid_property,
)
from icalendar.cal.component import Component
from icalendar.cal.examples import get_example
from icalendar.cal.timezone import Timezone
from icalendar.version import __version__

if TYPE_CHECKING:
    from datetime import date

    from icalendar.cal.event import Event
    from icalendar.cal.free_busy import FreeBusy
    from icalendar.cal.todo import Todo


class Calendar(Component):
    """
    The "VCALENDAR" object is a collection of calendar information.
    This information can include a variety of components, such as
    "VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY", "VTIMEZONE", or any
    other type of calendar component.
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
    def from_ical(cls, st, multiple=False):
        comps = Component.from_ical(st, multiple=True)
        all_timezones_so_far = True
        for comp in comps:
            for component in comp.subcomponents:
                if component.name == "VTIMEZONE":
                    if not all_timezones_so_far:
                        # If a preceding component refers to a VTIMEZONE defined
                        # later in the source st
                        # (forward references are allowed by RFC 5545), then the
                        # earlier component may have
                        # the wrong timezone attached.
                        # However, during computation of comps, all VTIMEZONEs
                        # observed do end up in
                        # the timezone cache. So simply re-running from_ical will
                        # rely on the cache
                        # for those forward references to produce the correct result.
                        # See test_create_america_new_york_forward_reference.
                        return Component.from_ical(st, multiple)
                else:
                    all_timezones_so_far = False

        # No potentially forward VTIMEZONEs to worry about
        if multiple:
            return comps
        if len(comps) > 1:
            raise ValueError(
                cls._format_error(
                    "Found multiple components where only one is allowed", st
                )
            )
        if len(comps) < 1:
            raise ValueError(
                cls._format_error(
                    "Found no components where exactly one is required", st
                )
            )
        return comps[0]

    @property
    def events(self) -> list[Event]:
        """All event components in the calendar.

        This is a shortcut to get all events.
        Modifications do not change the calendar.
        Use :py:meth:`Component.add_component`.

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
        Use :py:meth:`Component.add_component`.
        """
        return self.walk("VTODO")

    @property
    def freebusy(self) -> list[FreeBusy]:
        """All FreeBusy components in the calendar.

        This is a shortcut to get all FreeBusy.
        Modifications do not change the calendar.
        Use :py:meth:`Component.add_component`.
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
        """
        tzids = self.get_used_tzids()
        for timezone in self.timezones:
            tzids.remove(timezone.tz_name)
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

        .. note::

            Timezones that are not known will not be added.

        :param first_date: earlier than anything that happens in the calendar
        :param last_date: later than anything happening in the calendar

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
        for tzid in self.get_missing_tzids():
            try:
                timezone = Timezone.from_tzid(
                    tzid, first_date=first_date, last_date=last_date
                )
            except ValueError:
                continue
            self.add_component(timezone)

    calendar_name = multi_language_text_property(
        "NAME",
        "X-WR-CALNAME",
        """This property specifies the name of the calendar.

    This implements :rfc:`7986` ``NAME`` and ``X-WR-CALNAME``.

    Property Parameters:
        IANA, non-standard, alternate text
        representation, and language property parameters can be specified
        on this property.

    Conformance:
        This property can be specified multiple times in an
        iCalendar object.  However, each property MUST represent the name
        of the calendar in a different language.

    Description:
        This property is used to specify a name of the
        iCalendar object that can be used by calendar user agents when
        presenting the calendar data to a user.  Whilst a calendar only
        has a single name, multiple language variants can be specified by
        including this property multiple times with different "LANGUAGE"
        parameter values on each.

    Example:
        Below, we set the name of the calendar.

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.calendar_name = "My Calendar"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            NAME:My Calendar
            END:VCALENDAR
    """,
    )

    description = multi_language_text_property(
        "DESCRIPTION",
        "X-WR-CALDESC",
        """This property specifies the description of the calendar.

    This implements :rfc:`7986` ``DESCRIPTION`` and ``X-WR-CALDESC``.

    Conformance:
        This property can be specified multiple times in an
        iCalendar object.  However, each property MUST represent the
        description of the calendar in a different language.

    Description:
        This property is used to specify a lengthy textual
        description of the iCalendar object that can be used by calendar
        user agents when describing the nature of the calendar data to a
        user.  Whilst a calendar only has a single description, multiple
        language variants can be specified by including this property
        multiple times with different "LANGUAGE" parameter values on each.

    Example:
        Below, we add a description to a calendar.

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.description = "This is a calendar"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            DESCRIPTION:This is a calendar
            END:VCALENDAR
    """,
    )

    color = single_string_property(
        "COLOR",
        """This property specifies a color used for displaying the calendar.

    This implements :rfc:`7986` ``COLOR`` and ``X-APPLE-CALENDAR-COLOR``.
    Please note that since :rfc:`7986`, subcomponents can have their own color.

    Property Parameters:
        IANA and non-standard property parameters can
        be specified on this property.

    Conformance:
        This property can be specified once in an iCalendar
        object or in ``VEVENT``, ``VTODO``, or ``VJOURNAL`` calendar components.

    Description:
        This property specifies a color that clients MAY use
        when presenting the relevant data to a user.  Typically, this
        would appear as the "background" color of events or tasks.  The
        value is a case-insensitive color name taken from the CSS3 set of
        names, defined in Section 4.3 of `W3C.REC-css3-color-20110607 <https://www.w3.org/TR/css-color-3/>`_.

    Example:
        ``"turquoise"``, ``"#ffffff"``

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.color = "black"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            COLOR:black
            END:VCALENDAR

    """,
        "X-APPLE-CALENDAR-COLOR",
    )
    categories = categories_property
    uid = uid_property
    prodid = single_string_property(
        "PRODID",
        """PRODID specifies the identifier for the product that created the iCalendar object.

Conformance:
    The property MUST be specified once in an iCalendar object.

Description:
    The vendor of the implementation SHOULD assure that
    this is a globally unique identifier; using some technique such as
    an FPI value, as defined in [ISO.9070.1991].

    This property SHOULD NOT be used to alter the interpretation of an
    iCalendar object beyond the semantics specified in this memo.  For
    example, it is not to be used to further the understanding of non-
    standard properties.

Example:
    The following is an example of this property. It does not
    imply that English is the default language.

    .. code-block:: text

        -//ABC Corporation//NONSGML My Product//EN
""",  # noqa: E501
    )
    version = single_string_property(
        "VERSION",
        """VERSION of the calendar specification.

The default is ``"2.0"`` for :rfc:`5545`.

Purpose:
    This property specifies the identifier corresponding to the
    highest version number or the minimum and maximum range of the
    iCalendar specification that is required in order to interpret the
    iCalendar object.


      """,
    )

    calscale = single_string_property(
        "CALSCALE",
        """CALSCALE defines the calendar scale used for the calendar information specified in the iCalendar object.

Compatibility:
    :rfc:`7529` makes the case that GREGORIAN stays the default and other calendar scales
    are implemented on the RRULE.

Conformance:
    This property can be specified once in an iCalendar
    object.  The default value is "GREGORIAN".

Description:
    This memo is based on the Gregorian calendar scale.
    The Gregorian calendar scale is assumed if this property is not
    specified in the iCalendar object.  It is expected that other
    calendar scales will be defined in other specifications or by
    future versions of this memo.
        """,  # noqa: E501
        default="GREGORIAN",
    )
    method = single_string_property(
        "METHOD",
        """METHOD defines the iCalendar object method associated with the calendar object.

Description:
    When used in a MIME message entity, the value of this
    property MUST be the same as the Content-Type "method" parameter
    value.  If either the "METHOD" property or the Content-Type
    "method" parameter is specified, then the other MUST also be
    specified.

    No methods are defined by this specification.  This is the subject
    of other specifications, such as the iCalendar Transport-
    independent Interoperability Protocol (iTIP) defined by :rfc:`5546`.

    If this property is not present in the iCalendar object, then a
    scheduling transaction MUST NOT be assumed.  In such cases, the
    iCalendar object is merely being used to transport a snapshot of
    some calendar information; without the intention of conveying a
    scheduling semantic.
""",  # noqa: E501
    )

    @classmethod
    def new(
        cls,
        /,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        categories: Optional[Sequence[str]] = None,
        prodid: Optional[str] = f"-//collective//icalendar//{__version__}//EN",
        method: Optional[str] = None,
        version: str = "2.0",
        calscale: Optional[str] = None,
    ):
        calendar = cls()
        calendar.prodid = prodid
        calendar.version = version
        calendar.calendar_name = name
        calendar.color = color
        calendar.description = description
        calendar.method = method
        calendar.calscale = calscale
        calendar.categories = categories or []
        return calendar


__all__ = ["Calendar"]
