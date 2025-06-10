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

    Values:
        ``NEEDS_ACTION``,
        ``ACCEPTED``,
        ``DECLINED``,
        ``TENTATIVE``,
        ``DELEGATED``,
        ``COMPLETED``,
        ``IN_PROCESS``

    Purpose:
        To specify the participation status for the calendar user
        specified by the property.

    Description:
        This parameter can be specified on properties with a
        CAL-ADDRESS value type.  The parameter identifies the
        participation status for the calendar user specified by the
        property value.  The parameter values differ depending on whether
        they are associated with a group-scheduled "VEVENT", "VTODO", or
        "VJOURNAL".  The values MUST match one of the values allowed for
        the given calendar component.  If not specified on a property that
        allows this parameter, the default value is NEEDS-ACTION.
        Applications MUST treat x-name and iana-token values they don't
        recognize the same way as they would the NEEDS-ACTION value.
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

    Values:
        ``FREE``,
        ``BUSY``,
        ``BUSY_UNAVAILABLE``,
        ``BUSY_TENTATIVE``

    See also :class:`BUSYTYPE`.

    Purpose:
        To specify the free or busy time type.

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
    """

    FREE = "FREE"
    BUSY = "BUSY"
    BUSY_UNAVAILABLE = "BUSY-UNAVAILABLE"
    BUSY_TENTATIVE = "BUSY-TENTATIVE"


class CUTYPE(StrEnum):
    """Enum for CTYPE from :rfc:`5545`.

    Values:
        ``INDIVIDUAL``,
        ``GROUP``,
        ``RESOURCE``,
        ``ROOM``,
        ``UNKNOWN``

    Purpose:
        To identify the type of calendar user specified by the property.

    Description:
        This parameter can be specified on properties with a
        CAL-ADDRESS value type.  The parameter identifies the type of
        calendar user specified by the property.  If not specified on a
        property that allows this parameter, the default is INDIVIDUAL.
        Applications MUST treat x-name and iana-token values they don't
        recognize the same way as they would the UNKNOWN value.
    """

    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"
    RESOURCE = "RESOURCE"
    ROOM = "ROOM"
    UNKNOWN = "UNKNOWN"


class RELTYPE(StrEnum):
    """Enum for RELTYPE from :rfc:`5545`.

    Values:
        ``PARENT``,
        ``CHILD``,
        ``SIBLING``

    Purpose:
        To specify the type of hierarchical relationship associated
        with the calendar component specified by the property.

    Description:
        This parameter can be specified on a property that
        references another related calendar.  The parameter specifies the
        hierarchical relationship type of the calendar component
        referenced by the property.  The parameter value can be PARENT, to
        indicate that the referenced calendar component is a superior of
        calendar component; CHILD to indicate that the referenced calendar
        component is a subordinate of the calendar component; or SIBLING
        to indicate that the referenced calendar component is a peer of
        the calendar component.  If this parameter is not specified on an
        allowable property, the default relationship type is PARENT.
        Applications MUST treat x-name and iana-token values they don't
        recognize the same way as they would the PARENT value.

    """

    PARENT = "PARENT"
    CHILD = "CHILD"
    SIBLING = "SIBLING"


class RANGE(StrEnum):
    """Enum for RANGE from :rfc:`5545`.

    Values:
        ``THISANDFUTURE``,
        ``THISANDPRIOR`` (deprecated)

    Purpose:
        To specify the effective range of recurrence instances from
        the instance specified by the recurrence identifier specified by
        the property.

    Description:
        This parameter can be specified on a property that
        specifies a recurrence identifier.  The parameter specifies the
        effective range of recurrence instances that is specified by the
        property.  The effective range is from the recurrence identifier
        specified by the property.  If this parameter is not specified on
        an allowed property, then the default range is the single instance
        specified by the recurrence identifier value of the property.  The
        parameter value can only be "THISANDFUTURE" to indicate a range
        defined by the recurrence identifier and all subsequent instances.
        The value "THISANDPRIOR" is deprecated by this revision of
        iCalendar and MUST NOT be generated by applications.
    """

    THISANDFUTURE = "THISANDFUTURE"
    THISANDPRIOR = "THISANDPRIOR"  # deprecated


class RELATED(StrEnum):
    """Enum for RELATED from :rfc:`5545`.

    Values:
        ``START``,
        ``END``

    Purpose:
        To specify the relationship of the alarm trigger with
        respect to the start or end of the calendar component.

    Description:
        This parameter can be specified on properties that
        specify an alarm trigger with a "DURATION" value type.  The
        parameter specifies whether the alarm will trigger relative to the
        start or end of the calendar component.  The parameter value START
        will set the alarm to trigger off the start of the calendar
        component; the parameter value END will set the alarm to trigger
        off the end of the calendar component.  If the parameter is not
        specified on an allowable property, then the default is START.
    """

    START = "START"
    END = "END"


class ROLE(StrEnum):
    """Enum for ROLE from :rfc:`5545`.

    Values:
        ``CHAIR``,
        ``REQ_PARTICIPANT``,
        ``OPT_PARTICIPANT``,
        ``NON_PARTICIPANT``

    Purpose:
        To specify the participation role for the calendar user
        specified by the property.

    Description:
        This parameter can be specified on properties with a
        CAL-ADDRESS value type.  The parameter specifies the participation
        role for the calendar user specified by the property in the group
        schedule calendar component.  If not specified on a property that
        allows this parameter, the default value is REQ-PARTICIPANT.
        Applications MUST treat x-name and iana-token values they don't
        recognize the same way as they would the REQ-PARTICIPANT value.

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

class BUSYTYPE(StrEnum):
    """Enum for BUSYTYPE from :rfc:`7953`.

    Values:
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

    Values:
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
    "CLASS",
    "CUTYPE",
    "FBTYPE",
    "PARTSTAT",
    "RANGE",
    "RELATED",
    "RELTYPE",
    "ROLE",
    "VALUE",
]
