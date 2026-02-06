"""This module contains the parser/generators (or coders/encoders if you
prefer) for the classes/datatypes that are used in iCalendar:

###########################################################################

# This module defines these property value data types and property parameters

4.2 Defined property parameters are:

.. code-block:: text

     ALTREP, CN, CUTYPE, DELEGATED-FROM, DELEGATED-TO, DIR, ENCODING, FMTTYPE,
     FBTYPE, LANGUAGE, MEMBER, PARTSTAT, RANGE, RELATED, RELTYPE, ROLE, RSVP,
     SENT-BY, TZID, VALUE

4.3 Defined value data types are:

.. code-block:: text

    BINARY, BOOLEAN, CAL-ADDRESS, DATE, DATE-TIME, DURATION, FLOAT, INTEGER,
    PERIOD, RECUR, TEXT, TIME, URI, UTC-OFFSET

###########################################################################

iCalendar properties have values. The values are strongly typed. This module
defines these types, calling val.to_ical() on them will render them as defined
in rfc5545.

If you pass any of these classes a Python primitive, you will have an object
that can render itself as iCalendar formatted date.

Property Value Data Types start with a 'v'. they all have an to_ical() and
from_ical() method. The to_ical() method generates a text string in the
iCalendar format. The from_ical() method can parse this format and return a
primitive Python datatype. So it should always be true that:

.. code-block:: python

    x == vDataType.from_ical(VDataType(x).to_ical())

These types are mainly used for parsing and file generation. But you can set
them directly.
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from typing import TYPE_CHECKING, Any, ClassVar, TypeAlias

from icalendar.caselessdict import CaselessDict
from icalendar.enums import Enum
from icalendar.error import InvalidCalendar, JCalParsingError
from icalendar.parser import Parameters
from icalendar.parser_tools import (
    DEFAULT_ENCODING,
    ICAL_TYPE,
    SEQUENCE_TYPES,
    from_unicode,
    to_unicode,
)
from icalendar.timezone import tzid_from_dt, tzid_from_tzinfo, tzp
from icalendar.timezone.tzid import is_utc
from icalendar.tools import is_date, is_datetime, normalize_pytz, to_datetime

from .adr import AdrFields, vAdr
from .binary import vBinary
from .boolean import vBoolean
from .broken import vBrokenProperty
from .cal_address import vCalAddress
from .categories import vCategory
from .dt import TimeBase, vDDDLists, vDDDTypes
from .float import vFloat
from .geo import vGeo
from .inline import vInline
from .n import NFields, vN
from .org import vOrg
from .text import vText
from .uid import vUid
from .unknown import vUnknown
from .uri import vUri
from .xml_reference import vXmlReference

if TYPE_CHECKING:
    from icalendar.compatibility import Self

DURATION_REGEX = re.compile(
    r"([-+]?)P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$"
)

TIME_JCAL_REGEX = re.compile(
    r"^(?P<hour>[0-9]{2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})(?P<utc>Z)?$"
)


class vTime(TimeBase):
    """Time

    Value Name:
        TIME

    Purpose:
        This value type is used to identify values that contain a
        time of day.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            time         = time-hour time-minute time-second [time-utc]

            time-hour    = 2DIGIT        ;00-23
            time-minute  = 2DIGIT        ;00-59
            time-second  = 2DIGIT        ;00-60
            ;The "60" value is used to account for positive "leap" seconds.

            time-utc     = "Z"

    Description:
        If the property permits, multiple "time" values are
        specified by a COMMA-separated list of values.  No additional
        content value encoding (i.e., BACKSLASH character encoding, see
        vText) is defined for this value type.

        The "TIME" value type is used to identify values that contain a
        time of day.  The format is based on the [ISO.8601.2004] complete
        representation, basic format for a time of day.  The text format
        consists of a two-digit, 24-hour of the day (i.e., values 00-23),
        two-digit minute in the hour (i.e., values 00-59), and two-digit
        seconds in the minute (i.e., values 00-60).  The seconds value of
        60 MUST only be used to account for positive "leap" seconds.
        Fractions of a second are not supported by this format.

        In parallel to the "DATE-TIME" definition above, the "TIME" value
        type expresses time values in three forms:

        The form of time with UTC offset MUST NOT be used.  For example,
        the following is not valid for a time value:

        .. code-block:: text

            230000-0800        ;Invalid time format

        **FORM #1 LOCAL TIME**

        The local time form is simply a time value that does not contain
        the UTC designator nor does it reference a time zone.  For
        example, 11:00 PM:

        .. code-block:: text

            230000

        Time values of this type are said to be "floating" and are not
        bound to any time zone in particular.  They are used to represent
        the same hour, minute, and second value regardless of which time
        zone is currently being observed.  For example, an event can be
        defined that indicates that an individual will be busy from 11:00
        AM to 1:00 PM every day, no matter which time zone the person is
        in.  In these cases, a local time can be specified.  The recipient
        of an iCalendar object with a property value consisting of a local
        time, without any relative time zone information, SHOULD interpret
        the value as being fixed to whatever time zone the "ATTENDEE" is
        in at any given moment.  This means that two "Attendees", may
        participate in the same event at different UTC times; floating
        time SHOULD only be used where that is reasonable behavior.

        In most cases, a fixed time is desired.  To properly communicate a
        fixed time in a property value, either UTC time or local time with
        time zone reference MUST be specified.

        The use of local time in a TIME value without the "TZID" property
        parameter is to be interpreted as floating time, regardless of the
        existence of "VTIMEZONE" calendar components in the iCalendar
        object.

        **FORM #2: UTC TIME**

        UTC time, or absolute time, is identified by a LATIN CAPITAL
        LETTER Z suffix character, the UTC designator, appended to the
        time value.  For example, the following represents 07:00 AM UTC:

        .. code-block:: text

            070000Z

        The "TZID" property parameter MUST NOT be applied to TIME
        properties whose time values are specified in UTC.

        **FORM #3: LOCAL TIME AND TIME ZONE REFERENCE**

        The local time with reference to time zone information form is
        identified by the use the "TZID" property parameter to reference
        the appropriate time zone definition.

        Example:
            The following represents 8:30 AM in New York in winter,
            five hours behind UTC, in each of the three formats:

        .. code-block:: text

            083000
            133000Z
            TZID=America/New_York:083000
    """

    default_value: ClassVar[str] = "TIME"
    params: Parameters

    def __init__(self, *args, params: dict[str, Any] | None = None):
        if len(args) == 1:
            if not isinstance(args[0], (time, datetime)):
                raise ValueError(f"Expected a datetime.time, got: {args[0]}")
            self.dt = args[0]
        else:
            self.dt = time(*args)
        self.params = Parameters(params or {})
        self.params.update_tzid_from(self.dt)

    def to_ical(self):
        value = self.dt.strftime("%H%M%S")
        if self.is_utc():
            value += "Z"
        return value

    def is_utc(self) -> bool:
        """Whether this time is UTC."""
        return self.params.is_utc() or is_utc(self.dt)

    @staticmethod
    def from_ical(ical):
        # TODO: timezone support
        try:
            timetuple = (int(ical[:2]), int(ical[2:4]), int(ical[4:6]))
            return time(*timetuple)
        except Exception as e:
            raise ValueError(f"Expected time, got: {ical}") from e

    @classmethod
    def examples(cls) -> list[vTime]:
        """Examples of vTime."""
        return [cls(time(12, 30))]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        value = self.dt.strftime("%H:%M:%S")
        if self.is_utc():
            value += "Z"
        return [name, self.params.to_jcal(exclude_utc=True), self.VALUE.lower(), value]

    @classmethod
    def parse_jcal_value(cls, jcal: str) -> time:
        """Parse a jCal string to a :py:class:`datetime.time`.

        Raises:
            ~error.JCalParsingError: If it can't parse a time.
        """
        JCalParsingError.validate_value_type(jcal, str, cls)
        match = TIME_JCAL_REGEX.match(jcal)
        if match is None:
            raise JCalParsingError("Cannot parse time.", cls, value=jcal)
        hour = int(match.group("hour"))
        minute = int(match.group("minute"))
        second = int(match.group("second"))
        utc = bool(match.group("utc"))
        return time(hour, minute, second, tzinfo=timezone.utc if utc else None)

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            value = cls.parse_jcal_value(jcal_property[3])
        return cls(
            value,
            params=Parameters.from_jcal_property(jcal_property),
        )


UTC_OFFSET_JCAL_REGEX = re.compile(
    r"^(?P<sign>[+-])?(?P<hours>\d\d):(?P<minutes>\d\d)(?::(?P<seconds>\d\d))?$"
)


class vUTCOffset:
    """UTC Offset

    Value Name:
        UTC-OFFSET

    Purpose:
        This value type is used to identify properties that contain
        an offset from UTC to local time.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            utc-offset = time-numzone

            time-numzone = ("+" / "-") time-hour time-minute [time-second]

    Description:
        The PLUS SIGN character MUST be specified for positive
        UTC offsets (i.e., ahead of UTC).  The HYPHEN-MINUS character MUST
        be specified for negative UTC offsets (i.e., behind of UTC).  The
        value of "-0000" and "-000000" are not allowed.  The time-second,
        if present, MUST NOT be 60; if absent, it defaults to zero.

        Example:
            The following UTC offsets are given for standard time for
            New York (five hours behind UTC) and Geneva (one hour ahead of
            UTC):

        .. code-block:: text

            -0500

            +0100

        .. code-block:: pycon

            >>> from icalendar.prop import vUTCOffset
            >>> utc_offset = vUTCOffset.from_ical('-0500')
            >>> utc_offset
            datetime.timedelta(days=-1, seconds=68400)
            >>> utc_offset = vUTCOffset.from_ical('+0100')
            >>> utc_offset
            datetime.timedelta(seconds=3600)
    """

    default_value: ClassVar[str] = "UTC-OFFSET"
    params: Parameters

    ignore_exceptions = False  # if True, and we cannot parse this

    # component, we will silently ignore
    # it, rather than let the exception
    # propagate upwards

    def __init__(self, td: timedelta, /, params: dict[str, Any] | None = None):
        if not isinstance(td, timedelta):
            raise TypeError("Offset value MUST be a timedelta instance")
        self.td = td
        self.params = Parameters(params)

    def to_ical(self) -> str:
        """Return the ical representation."""
        return self.format("")

    def format(self, divider: str = "") -> str:
        """Represent the value with a possible divider.

        .. code-block:: pycon

            >>> from icalendar import vUTCOffset
            >>> from datetime import timedelta
            >>> utc_offset = vUTCOffset(timedelta(hours=-5))
            >>> utc_offset.format()
            '-0500'
            >>> utc_offset.format(divider=':')
            '-05:00'
        """
        if self.td < timedelta(0):
            sign = "-%s"
            td = timedelta(0) - self.td  # get timedelta relative to 0
        else:
            # Google Calendar rejects '0000' but accepts '+0000'
            sign = "+%s"
            td = self.td

        days, seconds = td.days, td.seconds

        hours = abs(days * 24 + seconds // 3600)
        minutes = abs((seconds % 3600) // 60)
        seconds = abs(seconds % 60)
        if seconds:
            duration = f"{hours:02}{divider}{minutes:02}{divider}{seconds:02}"
        else:
            duration = f"{hours:02}{divider}{minutes:02}"
        return sign % duration

    @classmethod
    def from_ical(cls, ical):
        if isinstance(ical, cls):
            return ical.td
        try:
            sign, hours, minutes, seconds = (
                ical[0:1],
                int(ical[1:3]),
                int(ical[3:5]),
                int(ical[5:7] or 0),
            )
            offset = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except Exception as e:
            raise ValueError(f"Expected UTC offset, got: {ical}") from e
        if not cls.ignore_exceptions and offset >= timedelta(hours=24):
            raise ValueError(f"Offset must be less than 24 hours, was {ical}")
        if sign == "-":
            return -offset
        return offset

    def __eq__(self, other):
        if not isinstance(other, vUTCOffset):
            return False
        return self.td == other.td

    def __hash__(self):
        return hash(self.td)

    def __repr__(self):
        return f"vUTCOffset({self.td!r})"

    @classmethod
    def examples(cls) -> list[vUTCOffset]:
        """Examples of vUTCOffset."""
        return [
            cls(timedelta(hours=3)),
            cls(timedelta(0)),
        ]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), self.format(":")]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Parameters:
            jcal_property: The jCal property to parse.

        Raises:
            ~error.JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        match = UTC_OFFSET_JCAL_REGEX.match(jcal_property[3])
        if match is None:
            raise JCalParsingError(f"Cannot parse {jcal_property!r} as UTC-OFFSET.")
        negative = match.group("sign") == "-"
        hours = int(match.group("hours"))
        minutes = int(match.group("minutes"))
        seconds = int(match.group("seconds") or 0)
        t = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        if negative:
            t = -t
        return cls(t, Parameters.from_jcal_property(jcal_property))


class TypesFactory(CaselessDict):
    """All Value types defined in RFC 5545 are registered in this factory
    class.

    The value and parameter names don't overlap. So one factory is enough for
    both kinds.
    """

    _instance: ClassVar[TypesFactory] = None

    def instance() -> TypesFactory:
        """Return a singleton instance of this class."""
        if TypesFactory._instance is None:
            TypesFactory._instance = TypesFactory()
        return TypesFactory._instance

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict"""
        super().__init__(*args, **kwargs)
        self.all_types = (
            vBinary,
            vBoolean,
            vCalAddress,
            vDDDLists,
            vDDDTypes,
            vDate,
            vDatetime,
            vDuration,
            vFloat,
            vFrequency,
            vGeo,
            vInline,
            vInt,
            vPeriod,
            vRecur,
            vText,
            vTime,
            vUTCOffset,
            vUri,
            vWeekday,
            vCategory,
            vAdr,
            vN,
            vOrg,
            vUid,
            vXmlReference,
            vUnknown,
        )
        self["binary"] = vBinary
        self["boolean"] = vBoolean
        self["cal-address"] = vCalAddress
        self["date"] = vDDDTypes
        self["date-time"] = vDDDTypes
        self["duration"] = vDDDTypes
        self["float"] = vFloat
        self["integer"] = vInt
        self["period"] = vPeriod
        self["recur"] = vRecur
        self["text"] = vText
        self["time"] = vTime
        self["uri"] = vUri
        self["utc-offset"] = vUTCOffset
        self["geo"] = vGeo
        self["inline"] = vInline
        self["date-time-list"] = vDDDLists
        self["categories"] = vCategory
        self["adr"] = vAdr  # RFC 6350 vCard
        self["n"] = vN  # RFC 6350 vCard
        self["org"] = vOrg  # RFC 6350 vCard
        self["unknown"] = vUnknown  # RFC 7265
        self["uid"] = vUid  # RFC 9253
        self["xml-reference"] = vXmlReference  # RFC 9253

    #################################################
    # Property types

    # These are the default types
    types_map = CaselessDict(
        {
            ####################################
            # Property value types
            # Calendar Properties
            "calscale": "text",
            "method": "text",
            "prodid": "text",
            "version": "text",
            # Descriptive Component Properties
            "attach": "uri",
            "categories": "categories",
            "class": "text",
            # vCard Properties (RFC 6350)
            "adr": "adr",
            "n": "n",
            "org": "org",
            "comment": "text",
            "description": "text",
            "geo": "geo",
            "location": "text",
            "percent-complete": "integer",
            "priority": "integer",
            "resources": "text",
            "status": "text",
            "summary": "text",
            # RFC 9253
            # link should be uri, xml-reference or uid
            # uri is likely most helpful if people forget to set VALUE
            "link": "uri",
            "concept": "uri",
            "refid": "text",
            # Date and Time Component Properties
            "completed": "date-time",
            "dtend": "date-time",
            "due": "date-time",
            "dtstart": "date-time",
            "duration": "duration",
            "freebusy": "period",
            "transp": "text",
            "refresh-interval": "duration",  # RFC 7986
            # Time Zone Component Properties
            "tzid": "text",
            "tzname": "text",
            "tzoffsetfrom": "utc-offset",
            "tzoffsetto": "utc-offset",
            "tzurl": "uri",
            # Relationship Component Properties
            "attendee": "cal-address",
            "contact": "text",
            "organizer": "cal-address",
            "recurrence-id": "date-time",
            "related-to": "text",
            "url": "uri",
            "conference": "uri",  # RFC 7986
            "source": "uri",
            "uid": "text",
            # Recurrence Component Properties
            "exdate": "date-time-list",
            "exrule": "recur",
            "rdate": "date-time-list",
            "rrule": "recur",
            # Alarm Component Properties
            "action": "text",
            "repeat": "integer",
            "trigger": "duration",
            "acknowledged": "date-time",
            # Change Management Component Properties
            "created": "date-time",
            "dtstamp": "date-time",
            "last-modified": "date-time",
            "sequence": "integer",
            # Miscellaneous Component Properties
            "request-status": "text",
            ####################################
            # parameter types (luckily there is no name overlap)
            "altrep": "uri",
            "cn": "text",
            "cutype": "text",
            "delegated-from": "cal-address",
            "delegated-to": "cal-address",
            "dir": "uri",
            "encoding": "text",
            "fmttype": "text",
            "fbtype": "text",
            "language": "text",
            "member": "cal-address",
            "partstat": "text",
            "range": "text",
            "related": "text",
            "reltype": "text",
            "role": "text",
            "rsvp": "boolean",
            "sent-by": "cal-address",
            "value": "text",
            # rfc 9253 parameters
            "label": "text",
            "linkrel": "text",
            "gap": "duration",
        }
    )

    def for_property(self, name, value_param: str | None = None) -> type:
        """Returns the type class for a property or parameter.

        Parameters:
            name: Property or parameter name
            value_param: Optional ``VALUE`` parameter, for example,
                "DATE", "DATE-TIME", or other string.

        Returns:
            The appropriate value type class.
        """
        # Special case: RDATE and EXDATE always use vDDDLists to support list values
        # regardless of the VALUE parameter
        if name.upper() in ("RDATE", "EXDATE"):  # and value_param is None:
            return self["date-time-list"]

        # Only use VALUE parameter for known properties that support multiple value
        # types (like DTSTART, DTEND, etc. which can be DATE or DATE-TIME)
        # For unknown/custom properties, always use the default type from types_map
        if value_param and name in self.types_map and value_param in self:
            return self[value_param]
        return self[self.types_map.get(name, "unknown")]

    def to_ical(self, name, value):
        """Encodes a named value from a primitive python type to an icalendar
        encoded string.
        """
        type_class = self.for_property(name)
        return type_class(value).to_ical()

    def from_ical(self, name, value):
        """Decodes a named property or parameter value from an icalendar
        encoded string to a primitive python type.
        """
        type_class = self.for_property(name)
        return type_class.from_ical(value)


VPROPERTY: TypeAlias = (
    vAdr
    | vBoolean
    | vBrokenProperty
    | vCalAddress
    | vCategory
    | vDDDLists
    | vDDDTypes
    | vDate
    | vDatetime
    | vDuration
    | vFloat
    | vFrequency
    | vInt
    | vMonth
    | vN
    | vOrg
    | vPeriod
    | vRecur
    | vSkip
    | vText
    | vTime
    | vUTCOffset
    | vUri
    | vWeekday
    | vInline
    | vBinary
    | vGeo
    | vUnknown
    | vXmlReference
    | vUid
)

__all__ = [
    "DURATION_REGEX",
    "VPROPERTY",
    "WEEKDAY_RULE",
    "AdrFields",
    "NFields",
    "TimeBase",
    "TypesFactory",
    "tzid_from_dt",
    "tzid_from_tzinfo",
    "vAdr",
    "vBinary",
    "vBoolean",
    "vBrokenProperty",
    "vCalAddress",
    "vCategory",
    "vDDDLists",
    "vDDDTypes",
    "vDate",
    "vDatetime",
    "vDuration",
    "vFloat",
    "vFrequency",
    "vGeo",
    "vInline",
    "vInt",
    "vMonth",
    "vN",
    "vOrg",
    "vPeriod",
    "vRecur",
    "vSkip",
    "vText",
    "vTime",
    "vUTCOffset",
    "vUid",
    "vUnknown",
    "vUri",
    "vWeekday",
    "vXmlReference",
]
