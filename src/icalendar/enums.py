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


__all__ = [
    "PARTSTAT",
    "FBTYPE",
    "CUTYPE",
    "RANGE",
    "RELATED",
    "ROLE",
    "RELTYPE",
]
