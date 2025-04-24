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
    """
    NEEDS_ACTION = "NEEDS-ACTION"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    TENTATIVE = "TENTATIVE"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    IN_PROCESS = "IN-PROCESS"


class FBTYPE(StrEnum):
    """Enum for FBTYPE from :rfc:`5545`."""
    FREE = "FREE"
    BUSY = "BUSY"
    BUSY_UNAVAILABLE = "BUSY-UNAVAILABLE"
    BUSY_TENTATIVE = "BUSY-TENTATIVE"


class CUTYPE(StrEnum):
    """Enum for CTYPE from :rfc:`5545`."""
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    RESOURCE = "RESOURCE"
    ROOM = "ROOM"
    UNKNOWN = "UNKNOWN"




class RANGE(StrEnum):
    """Enum for RANGE from :rfc:`5545`."""

    THISANDFUTURE = "THISANDFUTURE"
    THISANDPRIOR = "THISANDPRIOR"  # deprecated

class RELATED(StrEnum):
    """Enum for RELATED from :rfc:`5545`."""
    START = "START"
    END = "END"

class ROLE(StrEnum):
    """Enum for ROLE from :rfc:`5545`."""
    CHAIR = "CHAIR"
    REQ_PARTICIPANT = "REQ-PARTICIPANT"
    OPT_PARTICIPANT = "OPT-PARTICIPANT"
    NON_PARTICIPANT = "NON-PARTICIPANT"


__all__ = [
    "PARTSTAT",
    "FBTYPE",
    "CUTYPE",
    "RANGE",
    "RELATED",
    "ROLE",
]
