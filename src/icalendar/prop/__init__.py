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
