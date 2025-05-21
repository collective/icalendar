"""Enumerations for different types in the RFCs."""

from enum import Enum as _Enum


class Enum(_Enum):
    """Enum class that can be pickled."""

    def __reduce_ex__(self, _p):
        """For pickling."""
        return self.__class__, (self._name_,)


class StrEnum(str, Enum):
    """Enum for strings."""


class PARTSTAT(StrEnum):
    """Enum for PARTSTAT from :rfc:`5545`.

    Attributes:
        ``NEEDS_ACTION``,
        ``ACCEPTED``,
        ``DECLINED``,
        ``TENTATIVE``,
        ``DELEGATED``,
        ``COMPLETED``,
        ``IN_PROCESS``
    """

    NEEDS_ACTION = "NEEDS-ACTION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    TENTATIVE = "TENTATIVE"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    IN_PROCESS = "IN-PROCESS"


class FBTYPE(StrEnum):
    """Enum for FBTYPE from :rfc:`5545`.

    Attributes:
        ``FREE``,
        ``BUSY``,
        ``BUSY-UNAVAILABLE``,
        ``BUSY-TENTATIVE``
    """

    FREE = "FREE"
    BUSY = "BUSY"
    BUSY_UNAVAILABLE = "BUSY-UNAVAILABLE"
    BUSY_TENTATIVE = "BUSY-TENTATIVE"


class CUTYPE(StrEnum):
    """Enum for CTYPE from :rfc:`5545`.

    Attributes:
        ``INDIVIDUAL``,
        ``GROUP``,
        ``RESOURCE``,
        ``ROOM``,
        ``UNKNOWN``
    """

    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    RESOURCE = "RESOURCE"
    ROOM = "ROOM"
    UNKNOWN = "UNKNOWN"


class RELTYPE(StrEnum):
    """Enum for RELTYPE from :rfc:`5545`.

    Attributes:
        ``PARENT``,
        ``CHILD``,
        ``SIBLING``
    """

    PARENT = "PARENT"
    CHILD = "CHILD"
    SIBLING = "SIBLING"


class RANGE(StrEnum):
    """Enum for RANGE from :rfc:`5545`.

    Attributes:
        ``THISANDFUTURE``,
        ``THISANDPRIOR``
    """

    THISANDFUTURE = "THISANDFUTURE"
    THISANDPRIOR = "THISANDPRIOR"  # deprecated


class RELATED(StrEnum):
    """Enum for RELATED from :rfc:`5545`.

    Attributes:
        ``START``,
        ``END``
    """

    START = "START"
    END = "END"


class ROLE(StrEnum):
    """Enum for ROLE from :rfc:`5545`.

    Attributes:
        ``CHAIR``,
        ``REQ-PARTICIPANT``,
        ``OPT-PARTICIPANT``,
        ``NON-PARTICIPANT``
    """

    CHAIR = "CHAIR"
    REQ_PARTICIPANT = "REQ-PARTICIPANT"
    OPT_PARTICIPANT = "OPT-PARTICIPANT"
    NON_PARTICIPANT = "NON-PARTICIPANT"

class VALUE(StrEnum):
    """VALUE datatypes as defined in :rfc:`5545`.

    Attributes: ``BOOLEAN``, ``CAL_ADDRESS``, ``DATE``, ``DATE_TIME``, ``DURATION``,
    ``FLOAT``, ``INTEGER``, ``PERIOD``, ``RECUR``, ``TEXT``, ``TIME``, ``URI``,
    ``UTC_OFFSET``

    Description:
        This parameter specifies the value type and format of
        the property value.  The property values MUST be of a single value
        type.  For example, a "RDATE" property cannot have a combination
        of DATE-TIME and TIME value types.

        If the property's value is the default value type, then this
        parameter need not be specified.  However, if the property's
        default value type is overridden by some other allowable value
        type, then this parameter MUST be specified.

        Applications MUST preserve the value data for x-name and iana-
        token values that they don't recognize without attempting to
        interpret or parse the value data.

"""

    BOOLEAN = "BOOLEAN"
    CAL_ADDRESS = "CAL-ADDRESS"
    DATE = "DATE"
    DATE_TIME = "DATE-TIME"
    DURATION = "DURATION"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    PERIOD = "PERIOD"
    RECUR = "RECUR"
    TEXT = "TEXT"
    TIME = "TIME"
    URI = "URI"
    UTC_OFFSET = "UTC-OFFSET"

__all__ = [
    "CUTYPE",
    "FBTYPE",
    "PARTSTAT",
    "RANGE",
    "RELATED",
    "RELTYPE",
    "ROLE",
    "VALUE",
]
