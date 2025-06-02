"""Enumerations for different types in the RFCs."""

from enum import Enum as _Enum


class Enum(_Enum):
    """Enum class that can be pickled."""

    def __reduce_ex__(self, _p):
        """For pickling."""
        return self.__class__, (self._name_,)


class StrEnum(str, Enum):
    """Enum for strings."""

    def __str__(self) -> str:
        """Convert to a string.

        This is needed when we set the value directly in components.
        """
        return self.value


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

    See also :class:`BUSYTYPE`.
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
        ``REQ_PARTICIPANT``,
        ``OPT_PARTICIPANT``,
        ``NON_PARTICIPANT``
    """

    CHAIR = "CHAIR"
    REQ_PARTICIPANT = "REQ-PARTICIPANT"
    OPT_PARTICIPANT = "OPT-PARTICIPANT"
    NON_PARTICIPANT = "NON-PARTICIPANT"


class BUSYTYPE(StrEnum):
    """Enum for BUSYTYPE from :rfc:`7953`.

        Attributes:
            ``BUSY``,
            ``BUSY_UNAVAILABLE``,
            ``BUSY_TENTATIVE``

    Description:
        This property is used to specify the default busy time
        type.  The values correspond to those used by the :class:`FBTYPE`
        parameter used on a "FREEBUSY" property, with the exception that
        the "FREE" value is not used in this property.  If not specified
        on a component that allows this property, the default is "BUSY-
        UNAVAILABLE".

    Example:
        The following is an example of this property:

        .. code-block:: text

            BUSYTYPE:BUSY
    """

    BUSY = "BUSY"
    BUSY_UNAVAILABLE = "BUSY-UNAVAILABLE"
    BUSY_TENTATIVE = "BUSY-TENTATIVE"


class CLASS(StrEnum):
    """Enum for CLASS from :rfc:`5545`.

        Attributes:
            ``PUBLIC``,
            ``PRIVATE``,
            ``CONFIDENTIAL``

    Description:
        An access classification is only one component of the
        general security system within a calendar application.  It
        provides a method of capturing the scope of the access the
        calendar owner intends for information within an individual
        calendar entry.  The access classification of an individual
        iCalendar component is useful when measured along with the other
        security components of a calendar system (e.g., calendar user
        authentication, authorization, access rights, access role, etc.).
        Hence, the semantics of the individual access classifications
        cannot be completely defined by this memo alone.  Additionally,
        due to the "blind" nature of most exchange processes using this
        memo, these access classifications cannot serve as an enforcement
        statement for a system receiving an iCalendar object.  Rather,
        they provide a method for capturing the intention of the calendar
        owner for the access to the calendar component.  If not specified
        in a component that allows this property, the default value is
        PUBLIC.  Applications MUST treat x-name and iana-token values they
        don't recognize the same way as they would the PRIVATE value.
    """

    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    CONFIDENTIAL = "CONFIDENTIAL"


__all__ = [
    "BUSYTYPE",
    "CUTYPE",
    "FBTYPE",
    "PARTSTAT",
    "RANGE",
    "RELATED",
    "RELTYPE",
    "ROLE",
]
