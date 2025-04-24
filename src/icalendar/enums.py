"""Enumerations for different types in the RFCs."""
from enum import Enum


def _reduce_ex(self:Enum, _p):
    """For pickling."""
    return self.__class__, (self._name_,)



class PARTSTAT(str, Enum):
    """Enum for PARTSTAT from :rfc:`5545`.
    """
    NEEDS_ACTION = "NEEDS-ACTION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    TENTATIVE = "TENTATIVE"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    IN_PROCESS = "IN-PROCESS"

    __reduce_ex__ = _reduce_ex


class FBTYPE(str, Enum):
    """Enum for FBTYPE from :rfc:`5545`."""
    FREE = "FREE"
    BUSY = "BUSY"
    BUSY_UNAVAILABLE = "BUSY-UNAVAILABLE"
    BUSY_TENTATIVE = "BUSY-TENTATIVE"

    __reduce_ex__ = _reduce_ex


class CUTYPE(str, Enum):
    """Enum for CTYPE from :rfc:`5545`."""
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    RESOURCE = "RESOURCE"
    ROOM = "ROOM"
    UNKNOWN = "UNKNOWN"

    __reduce_ex__ = _reduce_ex


class SKIP(str, Enum):
    """Skip values for RRULE.

    These are defined in :rfc:`7529`.

    OMIT  is the default value.
    """

    OMIT = "OMIT"
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"

    __reduce_ex__ = _reduce_ex


class RANGE(str, Enum):
    """Enum for RANGE from :rfc:`5545`."""

    THISANDFUTURE = "THISANDFUTURE"
    THISANDPRIOR = "THISANDPRIOR"  # deprecated

class RELATED(str, Enum):
    """Enum for RELATED from :rfc:`5545`."""
    START = "START"
    END = "END"

class ROLE(str, Enum):
    """Enum for ROLE from :rfc:`5545`."""
    CHAIR = "CHAIR"
    REQ_PARTICIPANT = "REQ-PARTICIPANT"
    OPT_PARTICIPANT = "OPT-PARTICIPANT"
    NON_PARTICIPANT = "NON-PARTICIPANT"


__all__ = [
    "PARTSTAT",
    "FBTYPE",
    "CUTYPE",
    "SKIP",
    "RANGE",
    "RELATED",
    "ROLE",
]
