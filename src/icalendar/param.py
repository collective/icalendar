"""Parameter access for icalendar.

Related:

- :rfc:`5545`, Section 3.2. Property Parameters
- :rfc:`7986`, Section 6. Property Parameters
- https://github.com/collective/icalendar/issues/798
"""
from __future__ import annotations

from enum import Enum
import functools
from typing import TYPE_CHECKING, Callable, Optional, TypeVar, Union

if TYPE_CHECKING:
    from icalendar.parser import Parameters


class IcalendarProperty:
    """Interface provided by properties in icalendar.prop."""
    params: Parameters


def _default_return_none() -> Optional[str]:
    """Return None by default."""
    return None


def _default_return_string() -> str:
    """Return None by default."""
    return ""


def string_parameter(name:str, doc:str, default:Callable = _default_return_none,convert:Optional[Callable[[str], T]] = None) -> property:
    """Return a parameter with a quoted value (case sensitive)."""

    @functools.wraps(default)
    def fget(self: IcalendarProperty) -> Optional[str]:
        value = self.params.get(name)
        if value is None:
            return default()
        return convert(value) if convert else value

    def fset(self: IcalendarProperty, value: str):
        self.params[name] = convert(value) if convert else value

    def fdel(self: IcalendarProperty):
        self.params.pop(name, None)

    return property(fget,
                    fset, fdel, 
                    doc=doc)


ALTREP = string_parameter(
    "ALTREP",
    """ALTREP - Specify an alternate text representation for the property value.

Description:

    This parameter specifies a URI that points to an
    alternate representation for a textual property value.  A property
    specifying this parameter MUST also include a value that reflects
    the default representation of the text value.  The URI parameter
    value MUST be specified in a quoted-string.

.. note::

    While there is no restriction imposed on the URI schemes
    allowed for this parameter, Content Identifier (CID) :rfc:`2392`,
    HTTP :rfc:`2616`, and HTTPS :rfc:`2818` are the URI schemes most
    commonly used by current implementations.
""")

CN = string_parameter(
    "CN",
    """Specify the common name to be associated with the calendar user specified.

Description:

    This parameter can be specified on properties with a
    CAL-ADDRESS value type.  The parameter specifies the common name
    to be associated with the calendar user specified by the property.
    The parameter value is text.  The parameter value can be used for
    display text to be associated with the calendar address specified
    by the property.
""",
    default=_default_return_string
)

class CUTYPES(str, Enum):
    """Enum for CTYPE."""
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    RESOURCE = "RESOURCE"
    ROOM = "ROOM"
    UNKNOWN = "UNKNOWN"

def _default_return_individual() -> CUTYPES|str:
    """Default value."""
    return CUTYPES.INDIVIDUAL

def _convert_enum(enum: type[Enum]) -> Callable[[str], Enum]:

    def convert(value: str) -> str:
        """Convert if possible."""
        try:
            return enum(value.upper())
        except ValueError:
            return value
    return convert

CUTYPE = string_parameter(
    "CUTYPE",
    """Identify the type of calendar user specified by the property.

Description:

    This parameter can be specified on properties with a
    CAL-ADDRESS value type.  The parameter identifies the type of
    calendar user specified by the property.  If not specified on a
    property that allows this parameter, the default is INDIVIDUAL.
    Applications MUST treat x-name and iana-token values they don't
    recognize the same way as they would the UNKNOWN value.
""", default=_default_return_individual, convert=_convert_enum(CUTYPES))


def quoted_list_parameter(name: str, doc: str) -> property:
    """Return a parameter that contains a quoted list."""

    def fget(self: IcalendarProperty) -> tuple[str]:
        value = self.params.get(name)
        if value is None:
            return ()
        if isinstance(value, str):
            return tuple(value.split(","))
        return value

    def fset(self: IcalendarProperty, value: str|tuple[str]):
        if value == ():
            fdel(self)
        else:
            self.params[name] = (value,) if isinstance(value, str) else value

    def fdel(self: IcalendarProperty):
        self.params.pop(name, None)

    return property(fget, fset, fdel, doc=doc)


DELEGATED_FROM = quoted_list_parameter(
    "DELEGATED-FROM",
    """Specify the calendar users that have delegated their participation to the calendar user specified by the property.

Description:

    This parameter can be specified on properties with a
    CAL-ADDRESS value type.  This parameter specifies those calendar
    users that have delegated their participation in a group-scheduled
    event or to-do to the calendar user specified by the property.
    The individual calendar address parameter values MUST each be
    specified in a quoted-string.
""")

DELEGATED_TO = quoted_list_parameter(
    "DELEGATED-TO",
    """Specify the calendar users to whom the calendar user specified by the property has delegated participation.

Description:

    This parameter can be specified on properties with a
    CAL-ADDRESS value type.  This parameter specifies those calendar
    users whom have been delegated participation in a group-scheduled
    event or to-do by the calendar user specified by the property.
    The individual calendar address parameter values MUST each be
    specified in a quoted-string.
    """)

DIR = string_parameter(
    "DIR",
    """Specify reference to a directory entry associated with the calendar user specified by the property.

Description:

    This parameter can be specified on properties with a
    CAL-ADDRESS value type.  The parameter specifies a reference to
    the directory entry associated with the calendar user specified by
    the property.  The parameter value is a URI.  The URI parameter
    value MUST be specified in a quoted-string.

.. note::

    While there is no restriction imposed on the URI schemes
    allowed for this parameter, CID :rfc:`2392`, DATA :rfc:`2397`, FILE
    :rfc:`1738`, FTP :rfc:`1738`, HTTP :rfc:`2616`, HTTPS :rfc:`2818`, LDAP
    :rfc:`4516`, and MID :rfc:`2392` are the URI schemes most commonly
    used by current implementations.
""")

class FBTYPES(str, Enum):
    """Enum for FBTYPE."""
    FREE = "FREE"
    BUSY = "BUSY"
    BUSY_UNAVAILABLE = "BUSY-UNAVAILABLE"
    BUSY_TENTATIVE = "BUSY-TENTATIVE"

def _default_return_busy() -> FBTYPES|str:
    """Default value."""
    return FBTYPES.BUSY

FBTYPE = string_parameter(
    "FBTYPE",
    """Specify the free or busy time type.

Description:

    This parameter specifies the free or busy time type.
    The value FREE indicates that the time interval is free for
    scheduling.  The value BUSY indicates that the time interval is
    busy because one or more events have been scheduled for that
    interval.  The value BUSY-UNAVAILABLE indicates that the time
    interval is busy and that the interval can not be scheduled.  The
    value BUSY-TENTATIVE indicates that the time interval is busy
    because one or more events have been tentatively scheduled for
    that interval.  If not specified on a property that allows this
    parameter, the default is BUSY.  Applications MUST treat x-name
    and iana-token values they don't recognize the same way as they
    would the BUSY value.
""", default=_default_return_busy, convert=_convert_enum(FBTYPES))

LANGUAGE = string_parameter(
    "LANGUAGE",
    """Specify the language for text values in a property or property parameter.

Description:

    This parameter identifies the language of the text in
    the property value and of all property parameter values of the
    property.  The value of the "LANGUAGE" property parameter is that
    defined in :rfc:`5646`.

    For transport in a MIME entity, the Content-Language header field
    can be used to set the default language for the entire body part.
    Otherwise, no default language is assumed.
""")

__all__ = [
    "string_parameter",
    "quoted_list_parameter",
    "ALTREP",
    "CN",
    "CUTYPE",
    "CUTYPES",
    "DELEGATED_FROM",
    "DELEGATED_TO",
    "DIR",
    "FBTYPE",
    "FBTYPES",
    "LANGUAGE",
]
