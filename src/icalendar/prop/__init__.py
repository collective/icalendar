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

import base64
import binascii
import re
import uuid
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, ClassVar, Optional, Tuple, Union

from icalendar.caselessdict import CaselessDict
from icalendar.enums import Enum
from icalendar.error import InvalidCalendar, JCalParsingError
from icalendar.parser import Parameters, escape_char, unescape_char
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

try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

DURATION_REGEX = re.compile(
    r"([-+]?)P(?:(\d+)W)?(?:(\d+)D)?" r"(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$"
)

WEEKDAY_RULE = re.compile(
    r"(?P<signal>[+-]?)(?P<relative>[\d]{0,2})" r"(?P<weekday>[\w]{2})$"
)


class vBinary:
    """Binary property values are base 64 encoded."""

    default_value: ClassVar[str] = "BINARY"
    params: Parameters
    obj: str

    def __init__(self, obj, params: dict[str, str] | None = None):
        self.obj = to_unicode(obj)
        self.params = Parameters(encoding="BASE64", value="BINARY")
        if params:
            self.params.update(params)

    def __repr__(self):
        return f"vBinary({self.to_ical()})"

    def to_ical(self):
        return binascii.b2a_base64(self.obj.encode("utf-8"))[:-1]

    @staticmethod
    def from_ical(ical):
        try:
            return base64.b64decode(ical)
        except ValueError as e:
            raise ValueError("Not valid base 64 encoding.") from e

    def __eq__(self, other):
        """self == other"""
        return isinstance(other, vBinary) and self.obj == other.obj

    @classmethod
    def examples(cls) -> list[vBinary]:
        """Examples of vBinary."""
        return [cls("VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4")]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        params = self.params.to_jcal()
        if params.get("encoding") == "BASE64":
            # BASE64 is the only allowed encoding
            del params["encoding"]
        return [name, params, self.VALUE.lower(), self.obj]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> vBinary:
        """Parse jCal from :rfc:`7265` to a vBinary.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], str, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )


class vBoolean(int):
    """Boolean

    Value Name:  BOOLEAN

    Purpose:  This value type is used to identify properties that contain
      either a "TRUE" or "FALSE" Boolean value.

    Format Definition:  This value type is defined by the following
      notation:

    .. code-block:: text

        boolean    = "TRUE" / "FALSE"

    Description:  These values are case-insensitive text.  No additional
      content value encoding is defined for this value type.

    Example:  The following is an example of a hypothetical property that
      has a BOOLEAN value type:

    .. code-block:: python

        TRUE

    .. code-block:: pycon

        >>> from icalendar.prop import vBoolean
        >>> boolean = vBoolean.from_ical('TRUE')
        >>> boolean
        True
        >>> boolean = vBoolean.from_ical('FALSE')
        >>> boolean
        False
        >>> boolean = vBoolean.from_ical('True')
        >>> boolean
        True
    """

    default_value: ClassVar[str] = "BOOLEAN"
    params: Parameters

    BOOL_MAP = CaselessDict({"true": True, "false": False})

    def __new__(cls, *args, params: dict[str, Any] | None = None, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.params = Parameters(params)
        return self

    def to_ical(self):
        return b"TRUE" if self else b"FALSE"

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls.BOOL_MAP[ical]
        except Exception as e:
            raise ValueError(f"Expected 'TRUE' or 'FALSE'. Got {ical}") from e

    @classmethod
    def examples(cls) -> list[vBoolean]:
        """Examples of vBoolean."""
        return [
            cls(True),  # noqa: FBT003
            cls(False),  # noqa: FBT003
        ]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), bool(self)]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> vBoolean:
        """Parse jCal from :rfc:`7265` to a vBoolean.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], bool, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )


class vText(str):
    """Simple text."""

    default_value: ClassVar[str] = "TEXT"
    params: Parameters
    __slots__ = ("encoding", "params")

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.encoding = encoding
        self.params = Parameters(params)
        return self

    def __repr__(self) -> str:
        return f"vText({self.to_ical()!r})"

    def to_ical(self) -> bytes:
        return escape_char(self).encode(self.encoding)

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE):
        return cls(ical)

    @property
    def ical_value(self) -> str:
        """The string value of the text."""
        return str(self)

    from icalendar.param import ALTREP, GAP, LANGUAGE, RELTYPE, VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        if name == "request-status":  # TODO: maybe add a vRequestStatus class?
            return [name, {}, "text", self.split(";", 2)]
        return [name, self.params.to_jcal(), self.VALUE.lower(), str(self)]

    @classmethod
    def examples(cls):
        """Examples of vText."""
        return [cls("Hello World!")]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        name = jcal_property[0]
        if name == "categories":
            return vCategory.from_jcal(jcal_property)
        string = jcal_property[3]  # TODO: accept list or string but join with ;
        if name == "request-status":  # TODO: maybe add a vRequestStatus class?
            JCalParsingError.validate_list_type(jcal_property[3], str, cls, 3)
            string = ";".join(jcal_property[3])
        JCalParsingError.validate_value_type(string, str, cls, 3)
        return cls(
            string,
            params=Parameters.from_jcal_property(jcal_property),
        )

    @classmethod
    def parse_jcal_value(cls, jcal_value: Any) -> vText:
        """Parse a jCal value into a vText."""
        JCalParsingError.validate_value_type(jcal_value, (str, int, float), cls)
        return cls(str(jcal_value))


class vCalAddress(str):
    r"""Calendar User Address

    Value Name:
        CAL-ADDRESS

    Purpose:
        This value type is used to identify properties that contain a
        calendar user address.

    Description:
        The value is a URI as defined by [RFC3986] or any other
        IANA-registered form for a URI.  When used to address an Internet
        email transport address for a calendar user, the value MUST be a
        mailto URI, as defined by [RFC2368].

    Example:
        ``mailto:`` is in front of the address.

        .. code-block:: text

            mailto:jane_doe@example.com

        Parsing:

        .. code-block:: pycon

            >>> from icalendar import vCalAddress
            >>> cal_address = vCalAddress.from_ical('mailto:jane_doe@example.com')
            >>> cal_address
            vCalAddress('mailto:jane_doe@example.com')

        Encoding:

        .. code-block:: pycon

            >>> from icalendar import vCalAddress, Event
            >>> event = Event()
            >>> jane = vCalAddress("mailto:jane_doe@example.com")
            >>> jane.name = "Jane"
            >>> event["organizer"] = jane
            >>> print(event.to_ical().decode().replace('\\r\\n', '\\n').strip())
            BEGIN:VEVENT
            ORGANIZER;CN=Jane:mailto:jane_doe@example.com
            END:VEVENT
    """

    default_value: ClassVar[str] = "CAL-ADDRESS"
    params: Parameters
    __slots__ = ("params",)

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.params = Parameters(params)
        return self

    def __repr__(self):
        return f"vCalAddress('{self}')"

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical):
        return cls(ical)

    @property
    def ical_value(self):
        """The ``mailto:`` part of the address."""
        return str(self)

    @property
    def email(self) -> str:
        """The email address without ``mailto:`` at the start."""
        if self.lower().startswith("mailto:"):
            return self[7:]
        return str(self)

    from icalendar.param import (
        CN,
        CUTYPE,
        DELEGATED_FROM,
        DELEGATED_TO,
        DIR,
        LANGUAGE,
        PARTSTAT,
        ROLE,
        RSVP,
        SENT_BY,
        VALUE,
    )

    name = CN

    @staticmethod
    def _get_email(email: str) -> str:
        """Extract email and add mailto: prefix if needed.

        Handles case-insensitive mailto: prefix checking.

        Args:
            email: Email string that may or may not have mailto: prefix

        Returns:
            Email string with mailto: prefix
        """
        if not email.lower().startswith("mailto:"):
            return f"mailto:{email}"
        return email

    @classmethod
    def new(
        cls,
        email: str,
        /,
        cn: str | None = None,
        cutype: str | None = None,
        delegated_from: str | None = None,
        delegated_to: str | None = None,
        directory: str | None = None,
        language: str | None = None,
        partstat: str | None = None,
        role: str | None = None,
        rsvp: bool | None = None,
        sent_by: str | None = None,
    ):
        """Create a new vCalAddress with RFC 5545 parameters.

        Creates a vCalAddress instance with automatic mailto: prefix handling
        and support for all standard RFC 5545 parameters.

        Args:
            email: The email address (mailto: prefix added automatically if missing)
            cn: Common Name parameter
            cutype: Calendar user type (INDIVIDUAL, GROUP, RESOURCE, ROOM)
            delegated_from: Email of the calendar user that delegated
            delegated_to: Email of the calendar user that was delegated to
            directory: Reference to directory information
            language: Language for text values
            partstat: Participation status (NEEDS-ACTION, ACCEPTED, DECLINED, etc.)
            role: Role (REQ-PARTICIPANT, OPT-PARTICIPANT, NON-PARTICIPANT, CHAIR)
            rsvp: Whether RSVP is requested
            sent_by: Email of the calendar user acting on behalf of this user

        Returns:
            vCalAddress: A new calendar address with specified parameters

        Raises:
            TypeError: If email is not a string

        Examples:
            Basic usage:

            >>> from icalendar.prop import vCalAddress
            >>> addr = vCalAddress.new("test@test.com")
            >>> str(addr)
            'mailto:test@test.com'

            With parameters:

            >>> addr = vCalAddress.new("test@test.com", cn="Test User", role="CHAIR")
            >>> addr.params["CN"]
            'Test User'
            >>> addr.params["ROLE"]
            'CHAIR'
        """
        if not isinstance(email, str):
            raise TypeError(f"Email must be a string, not {type(email).__name__}")

        # Handle mailto: prefix (case-insensitive)
        email_with_prefix = cls._get_email(email)

        # Create the address
        addr = cls(email_with_prefix)

        # Set parameters if provided
        if cn is not None:
            addr.params["CN"] = cn
        if cutype is not None:
            addr.params["CUTYPE"] = cutype
        if delegated_from is not None:
            addr.params["DELEGATED-FROM"] = cls._get_email(delegated_from)
        if delegated_to is not None:
            addr.params["DELEGATED-TO"] = cls._get_email(delegated_to)
        if directory is not None:
            addr.params["DIR"] = directory
        if language is not None:
            addr.params["LANGUAGE"] = language
        if partstat is not None:
            addr.params["PARTSTAT"] = partstat
        if role is not None:
            addr.params["ROLE"] = role
        if rsvp is not None:
            addr.params["RSVP"] = "TRUE" if rsvp else "FALSE"
        if sent_by is not None:
            addr.params["SENT-BY"] = cls._get_email(sent_by)

        return addr

    def to_jcal(self, name: str) -> list:
        """Return this property in jCal format."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), self.ical_value]

    @classmethod
    def examples(cls) -> list[vCalAddress]:
        """Examples of vCalAddress."""
        return [cls.new("you@example.org", cn="You There")]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], str, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )


class vFloat(float):
    """Float

    Value Name:
        FLOAT

    Purpose:
        This value type is used to identify properties that contain
        a real-number value.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            float      = (["+"] / "-") 1*DIGIT ["." 1*DIGIT]

    Description:
        If the property permits, multiple "float" values are
        specified by a COMMA-separated list of values.

        Example:

        .. code-block:: text

            1000000.0000001
            1.333
            -3.14

        .. code-block:: pycon

            >>> from icalendar.prop import vFloat
            >>> float = vFloat.from_ical('1000000.0000001')
            >>> float
            1000000.0000001
            >>> float = vFloat.from_ical('1.333')
            >>> float
            1.333
            >>> float = vFloat.from_ical('+1.333')
            >>> float
            1.333
            >>> float = vFloat.from_ical('-3.14')
            >>> float
            -3.14
    """

    default_value: ClassVar[str] = "FLOAT"
    params: Parameters

    def __new__(cls, *args, params: dict[str, Any] | None = None, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.params = Parameters(params)
        return self

    def to_ical(self):
        return str(self).encode("utf-8")

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical)
        except Exception as e:
            raise ValueError(f"Expected float value, got: {ical}") from e

    @classmethod
    def examples(cls) -> list[vFloat]:
        """Examples of vFloat."""
        return [vFloat(3.1415)]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), float(self)]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the jCal provided is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        if jcal_property[0].upper() == "GEO":
            return vGeo.from_jcal(jcal_property)
        JCalParsingError.validate_value_type(jcal_property[3], float, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )


class vInt(int):
    """Integer

    Value Name:
        INTEGER

    Purpose:
        This value type is used to identify properties that contain a
        signed integer value.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            integer    = (["+"] / "-") 1*DIGIT

    Description:
        If the property permits, multiple "integer" values are
        specified by a COMMA-separated list of values.  The valid range
        for "integer" is -2147483648 to 2147483647.  If the sign is not
        specified, then the value is assumed to be positive.

        Example:

        .. code-block:: text

            1234567890
            -1234567890
            +1234567890
            432109876

        .. code-block:: pycon

            >>> from icalendar.prop import vInt
            >>> integer = vInt.from_ical('1234567890')
            >>> integer
            1234567890
            >>> integer = vInt.from_ical('-1234567890')
            >>> integer
            -1234567890
            >>> integer = vInt.from_ical('+1234567890')
            >>> integer
            1234567890
            >>> integer = vInt.from_ical('432109876')
            >>> integer
            432109876
    """

    default_value: ClassVar[str] = "INTEGER"
    params: Parameters

    def __new__(cls, *args, params: dict[str, Any] | None = None, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.params = Parameters(params)
        return self

    def to_ical(self) -> bytes:
        return str(self).encode("utf-8")

    @classmethod
    def from_ical(cls, ical: ICAL_TYPE):
        try:
            return cls(ical)
        except Exception as e:
            raise ValueError(f"Expected int, got: {ical}") from e

    @classmethod
    def examples(cls) -> list[vInt]:
        """Examples of vInt."""
        return [vInt(1000), vInt(-42)]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), int(self)]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        JCalParsingError.validate_value_type(jcal_property[3], int, cls, 3)
        return cls(
            jcal_property[3],
            params=Parameters.from_jcal_property(jcal_property),
        )

    @classmethod
    def parse_jcal_value(cls, value: Any) -> int:
        """Parse a jCal value for vInt.

        Raises:
            JCalParsingError: If the value is not an int.
        """
        JCalParsingError.validate_value_type(value, int, cls)
        return cls(value)


class vDDDLists:
    """A list of vDDDTypes values."""

    default_value: ClassVar[str] = "DATE-TIME"
    params: Parameters
    dts: list[vDDDTypes]

    def __init__(self, dt_list, params: dict[str, Any] | None = None):
        if params is None:
            params = {}
        if not hasattr(dt_list, "__iter__"):
            dt_list = [dt_list]
        vddd = []
        tzid = None
        for dt_l in dt_list:
            dt = vDDDTypes(dt_l) if not isinstance(dt_l, vDDDTypes) else dt_l
            vddd.append(dt)
            if "TZID" in dt.params:
                tzid = dt.params["TZID"]

        if tzid:
            # NOTE: no support for multiple timezones here!
            params["TZID"] = tzid
        self.params = Parameters(params)
        self.dts = vddd

    def to_ical(self):
        dts_ical = (from_unicode(dt.to_ical()) for dt in self.dts)
        return b",".join(dts_ical)

    @staticmethod
    def from_ical(ical, timezone=None):
        out = []
        ical_dates = ical.split(",")
        for ical_dt in ical_dates:
            out.append(vDDDTypes.from_ical(ical_dt, timezone=timezone))
        return out

    def __eq__(self, other):
        if isinstance(other, vDDDLists):
            return self.dts == other.dts
        if isinstance(other, (TimeBase, date)):
            return self.dts == [other]
        return False

    def __repr__(self):
        """String representation."""
        return f"{self.__class__.__name__}({self.dts})"

    @classmethod
    def examples(cls) -> list[vDDDLists]:
        """Examples of vDDDLists."""
        return [vDDDLists([datetime(2025, 11, 10, 16, 50)])]  # noqa: DTZ001

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [
            name,
            self.params.to_jcal(),
            self.VALUE.lower(),
            *[dt.to_jcal(name)[3] for dt in self.dts],
        ]

    def _get_value(self) -> str | None:
        return None if not self.dts else self.dts[0].VALUE

    from icalendar.param import VALUE

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the jCal provided is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        values = jcal_property[3:]
        prop = jcal_property[:3]
        dts = []
        for value in values:
            dts.append(vDDDTypes.from_jcal(prop + [value]))
        return cls(
            dts,
            params=Parameters.from_jcal_property(jcal_property),
        )


class vCategory:
    default_value: ClassVar[str] = "TEXT"
    params: Parameters

    def __init__(
        self, c_list: list[str] | str, /, params: dict[str, Any] | None = None
    ):
        if not hasattr(c_list, "__iter__") or isinstance(c_list, str):
            c_list = [c_list]
        self.cats: list[vText | str] = [vText(c) for c in c_list]
        self.params = Parameters(params)

    def __iter__(self):
        return iter(vCategory.from_ical(self.to_ical()))

    def to_ical(self):
        return b",".join(
            [
                c.to_ical() if hasattr(c, "to_ical") else vText(c).to_ical()
                for c in self.cats
            ]
        )

    @staticmethod
    def from_ical(ical):
        ical = to_unicode(ical)
        return ical.split(",")

    def __eq__(self, other):
        """self == other"""
        return isinstance(other, vCategory) and self.cats == other.cats

    def __repr__(self):
        """String representation."""
        return f"{self.__class__.__name__}({self.cats}, params={self.params})"

    def to_jcal(self, name: str) -> list:
        """The jCal representation for categories."""
        result = [name, self.params.to_jcal(), self.VALUE.lower()]
        result.extend(map(str, self.cats))
        if not self.cats:
            result.append("")
        return result

    @classmethod
    def examples(cls) -> list[vCategory]:
        """Examples of vCategory."""
        return [cls(["HOME", "COSY"])]

    from icalendar.param import VALUE

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        for i, category in enumerate(jcal_property[3:], start=3):
            JCalParsingError.validate_value_type(category, str, cls, i)
        return cls(
            jcal_property[3:],
            Parameters.from_jcal_property(jcal_property),
        )


class TimeBase:
    """Make classes with a datetime/date comparable."""

    default_value: ClassVar[str]
    params: Parameters
    ignore_for_equality = {"TZID", "VALUE"}

    def __eq__(self, other):
        """self == other"""
        if isinstance(other, date):
            return self.dt == other
        if isinstance(other, TimeBase):
            default = object()
            for key in (
                set(self.params) | set(other.params)
            ) - self.ignore_for_equality:
                if key[:2].lower() != "x-" and self.params.get(
                    key, default
                ) != other.params.get(key, default):
                    return False
            return self.dt == other.dt
        if isinstance(other, vDDDLists):
            return other == self
        return False

    def __hash__(self):
        return hash(self.dt)

    from icalendar.param import RANGE, RELATED, TZID

    def __repr__(self):
        """String representation."""
        return f"{self.__class__.__name__}({self.dt}, {self.params})"


DT_TYPE: TypeAlias = Union[
    datetime,
    date,
    timedelta,
    time,
    Tuple[datetime, datetime],
    Tuple[datetime, timedelta],
]


class vDDDTypes(TimeBase):
    """A combined Datetime, Date or Duration parser/generator. Their format
    cannot be confused, and often values can be of either types.
    So this is practical.
    """

    default_value: ClassVar[str] = "DATE-TIME"
    params: Parameters
    dt: DT_TYPE

    def __init__(self, dt, params: Optional[dict[str, Any]] = None):
        if params is None:
            params = {}
        if not isinstance(dt, (datetime, date, timedelta, time, tuple)):
            raise TypeError(
                "You must use datetime, date, timedelta, time or tuple (for periods)"
            )
        self.dt = dt
        # if isinstance(dt, (datetime, timedelta)): pass
        if is_date(dt):
            params.update({"value": "DATE"})
        elif isinstance(dt, time):
            params.update({"value": "TIME"})
        elif isinstance(dt, tuple):
            params.update({"value": "PERIOD"})
        self.params = Parameters(params)
        self.params.update_tzid_from(dt)

    def to_property_type(self) -> vDatetime | vDate | vDuration | vTime | vPeriod:
        """Convert to a property type.

        Raises:
            ValueError: If the type is unknown.
        """
        dt = self.dt
        if isinstance(dt, datetime):
            result = vDatetime(dt)
        elif isinstance(dt, date):
            result = vDate(dt)
        elif isinstance(dt, timedelta):
            result = vDuration(dt)
        elif isinstance(dt, time):
            result = vTime(dt)
        elif isinstance(dt, tuple) and len(dt) == 2:
            result = vPeriod(dt)
        else:
            raise ValueError(f"Unknown date type: {type(dt)}")
        result.params = self.params
        return result

    def to_ical(self) -> str:
        """Return the ical representation."""
        return self.to_property_type().to_ical()

    @classmethod
    def from_ical(cls, ical, timezone=None):
        if isinstance(ical, cls):
            return ical.dt
        u = ical.upper()
        if u.startswith(("P", "-P", "+P")):
            return vDuration.from_ical(ical)
        if "/" in u:
            return vPeriod.from_ical(ical, timezone=timezone)

        if len(ical) in (15, 16):
            return vDatetime.from_ical(ical, timezone=timezone)
        if len(ical) == 8:
            if timezone:
                tzinfo = tzp.timezone(timezone)
                if tzinfo is not None:
                    return to_datetime(vDate.from_ical(ical)).replace(tzinfo=tzinfo)
            return vDate.from_ical(ical)
        if len(ical) in (6, 7):
            return vTime.from_ical(ical)
        raise ValueError(f"Expected datetime, date, or time. Got: '{ical}'")

    @property
    def td(self) -> timedelta:
        """Compatibility property returning ``self.dt``.

        This class is used to replace different time components.
        Some of them contain a datetime or date (``.dt``).
        Some of them contain a timedelta (``.td``).
        This property allows interoperability.
        """
        return self.dt

    @property
    def dts(self) -> list:
        """Compatibility method to return a list of datetimes."""
        return [self]

    @classmethod
    def examples(cls) -> list[vDDDTypes]:
        """Examples of vDDDTypes."""
        return [cls(date(2025, 11, 10))]

    def _get_value(self) -> str | None:
        """Determine the VALUE parameter."""
        return self.to_property_type().VALUE

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return self.to_property_type().to_jcal(name)

    @classmethod
    def parse_jcal_value(cls, jcal: str | list) -> timedelta:
        """Parse a jCal value.

        Raises:
            JCalParsingError: If the value can't be parsed as either a date, time,
                date-time, duration, or period.
        """
        if isinstance(jcal, list):
            return vPeriod.parse_jcal_value(jcal)
        JCalParsingError.validate_value_type(jcal, str, cls)
        if "/" in jcal:
            return vPeriod.parse_jcal_value(jcal)
        for jcal_type in (vDatetime, vDate, vTime, vDuration):
            try:
                return jcal_type.parse_jcal_value(jcal)
            except JCalParsingError:  # noqa: PERF203
                pass
        raise JCalParsingError(
            "Cannot parse date, time, date-time, duration, or period.", cls, value=jcal
        )

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            dt = cls.parse_jcal_value(jcal_property[3])
        params = Parameters.from_jcal_property(jcal_property)
        if params.tzid:
            if isinstance(dt, tuple):
                # period
                start = tzp.localize(dt[0], params.tzid)
                end = tzp.localize(dt[1], params.tzid) if is_datetime(dt[1]) else dt[1]
                dt = (start, end)
            else:
                dt = tzp.localize(dt, params.tzid)
        return cls(
            dt,
            params=params,
        )


class vDate(TimeBase):
    """Date

    Value Name:
        DATE

    Purpose:
        This value type is used to identify values that contain a
        calendar date.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            date               = date-value

            date-value         = date-fullyear date-month date-mday
            date-fullyear      = 4DIGIT
            date-month         = 2DIGIT        ;01-12
            date-mday          = 2DIGIT        ;01-28, 01-29, 01-30, 01-31
                                               ;based on month/year

    Description:
        If the property permits, multiple "date" values are
        specified as a COMMA-separated list of values.  The format for the
        value type is based on the [ISO.8601.2004] complete
        representation, basic format for a calendar date.  The textual
        format specifies a four-digit year, two-digit month, and two-digit
        day of the month.  There are no separator characters between the
        year, month, and day component text.

    Example:
        The following represents July 14, 1997:

        .. code-block:: text

            19970714

        .. code-block:: pycon

            >>> from icalendar.prop import vDate
            >>> date = vDate.from_ical('19970714')
            >>> date.year
            1997
            >>> date.month
            7
            >>> date.day
            14
    """

    default_value: ClassVar[str] = "DATE"
    params: Parameters

    def __init__(self, dt, params: Optional[dict[str, Any]] = None):
        if not isinstance(dt, date):
            raise TypeError("Value MUST be a date instance")
        self.dt = dt
        self.params = Parameters(params or {})

    def to_ical(self):
        s = f"{self.dt.year:04}{self.dt.month:02}{self.dt.day:02}"
        return s.encode("utf-8")

    @staticmethod
    def from_ical(ical):
        try:
            timetuple = (
                int(ical[:4]),  # year
                int(ical[4:6]),  # month
                int(ical[6:8]),  # day
            )
            return date(*timetuple)
        except Exception as e:
            raise ValueError(f"Wrong date format {ical}") from e

    @classmethod
    def examples(cls) -> list[vDate]:
        """Examples of vDate."""
        return [cls(date(2025, 11, 10))]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [
            name,
            self.params.to_jcal(),
            self.VALUE.lower(),
            self.dt.strftime("%Y-%m-%d"),
        ]

    @classmethod
    def parse_jcal_value(cls, jcal: str) -> datetime:
        """Parse a jCal string to a :py:class:`datetime.datetime`.

        Raises:
            JCalParsingError: If it can't parse a date.
        """
        JCalParsingError.validate_value_type(jcal, str, cls)
        try:
            return datetime.strptime(jcal, "%Y-%m-%d").date()  # noqa: DTZ007
        except ValueError as e:
            raise JCalParsingError("Cannot parse date.", cls, value=jcal) from e

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            value = cls.parse_jcal_value(jcal_property[3])
        return cls(
            value,
            params=Parameters.from_jcal_property(jcal_property),
        )


class vDatetime(TimeBase):
    """Date-Time

    Value Name:
        DATE-TIME

    Purpose:
        This value type is used to identify values that specify a
        precise calendar date and time of day. The format is based on
        the ISO.8601.2004 complete representation.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            date-time  = date "T" time

            date       = date-value
            date-value         = date-fullyear date-month date-mday
            date-fullyear      = 4DIGIT
            date-month         = 2DIGIT        ;01-12
            date-mday          = 2DIGIT        ;01-28, 01-29, 01-30, 01-31
                                               ;based on month/year
            time               = time-hour time-minute time-second [time-utc]
            time-hour          = 2DIGIT        ;00-23
            time-minute        = 2DIGIT        ;00-59
            time-second        = 2DIGIT        ;00-60
            time-utc           = "Z"

        The following is the representation of the date-time format.

        .. code-block:: text

            YYYYMMDDTHHMMSS

    Description:
        vDatetime is timezone aware and uses a timezone library.
        When a vDatetime object is created from an
        ical string, you can pass a valid timezone identifier. When a
        vDatetime object is created from a Python :py:mod:`datetime` object, it uses the
        tzinfo component, if present. Otherwise a timezone-naive object is
        created. Be aware that there are certain limitations with timezone naive
        DATE-TIME components in the icalendar standard.

    Example:
        The following represents March 2, 2021 at 10:15 AM with local time:

        .. code-block:: pycon

            >>> from icalendar import vDatetime
            >>> datetime = vDatetime.from_ical("20210302T101500")
            >>> datetime.tzname()
            >>> datetime.year
            2021
            >>> datetime.minute
            15

        The following represents March 2, 2021 at 10:15 AM in New York:

        .. code-block:: pycon

            >>> datetime = vDatetime.from_ical("20210302T101500", 'America/New_York')
            >>> datetime.tzname()
            'EST'

        The following represents March 2, 2021 at 10:15 AM in Berlin:

        .. code-block:: pycon

            >>> from zoneinfo import ZoneInfo
            >>> timezone = ZoneInfo("Europe/Berlin")
            >>> vDatetime.from_ical("20210302T101500", timezone)
            datetime.datetime(2021, 3, 2, 10, 15, tzinfo=ZoneInfo(key='Europe/Berlin'))
    """

    default_value: ClassVar[str] = "DATE-TIME"
    params: Parameters

    def __init__(self, dt, /, params: dict[str, Any] | None = None):
        self.dt = dt
        self.params = Parameters(params)
        self.params.update_tzid_from(dt)

    def to_ical(self):
        dt = self.dt

        s = (
            f"{dt.year:04}{dt.month:02}{dt.day:02}"
            f"T{dt.hour:02}{dt.minute:02}{dt.second:02}"
        )
        if self.is_utc():
            s += "Z"
        return s.encode("utf-8")

    @staticmethod
    def from_ical(ical, timezone=None):
        """Create a datetime from the RFC string."""
        tzinfo = None
        if isinstance(timezone, str):
            tzinfo = tzp.timezone(timezone)
        elif timezone is not None:
            tzinfo = timezone

        try:
            timetuple = (
                int(ical[:4]),  # year
                int(ical[4:6]),  # month
                int(ical[6:8]),  # day
                int(ical[9:11]),  # hour
                int(ical[11:13]),  # minute
                int(ical[13:15]),  # second
            )
            if tzinfo:
                return tzp.localize(datetime(*timetuple), tzinfo)  # noqa: DTZ001
            if not ical[15:]:
                return datetime(*timetuple)  # noqa: DTZ001
            if ical[15:16] == "Z":
                return tzp.localize_utc(datetime(*timetuple))  # noqa: DTZ001
        except Exception as e:
            raise ValueError(f"Wrong datetime format: {ical}") from e
        raise ValueError(f"Wrong datetime format: {ical}")

    @classmethod
    def examples(cls) -> list[vDatetime]:
        """Examples of vDatetime."""
        return [cls(datetime(2025, 11, 10, 16, 52))]  # noqa: DTZ001

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        value = self.dt.strftime("%Y-%m-%dT%H:%M:%S")
        if self.is_utc():
            value += "Z"
        return [name, self.params.to_jcal(exclude_utc=True), self.VALUE.lower(), value]

    def is_utc(self) -> bool:
        """Whether this datetime is UTC."""
        return self.params.is_utc() or is_utc(self.dt)

    @classmethod
    def parse_jcal_value(cls, jcal: str) -> datetime:
        """Parse a jCal string to a :py:class:`datetime.datetime`.

        Raises:
            JCalParsingError: If it can't parse a date-time value.
        """
        JCalParsingError.validate_value_type(jcal, str, cls)
        utc = jcal.endswith("Z")
        if utc:
            jcal = jcal[:-1]
        try:
            dt = datetime.strptime(jcal, "%Y-%m-%dT%H:%M:%S")  # noqa: DTZ007
        except ValueError as e:
            raise JCalParsingError("Cannot parse date-time.", cls, value=jcal) from e
        if utc:
            return tzp.localize_utc(dt)
        return dt

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        params = Parameters.from_jcal_property(jcal_property)
        with JCalParsingError.reraise_with_path_added(3):
            dt = cls.parse_jcal_value(jcal_property[3])
        if params.tzid:
            dt = tzp.localize(dt, params.tzid)
        return cls(
            dt,
            params=params,
        )


class vDuration(TimeBase):
    """Duration

    Value Name:
        DURATION

    Purpose:
        This value type is used to identify properties that contain
        a duration of time.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            dur-value  = (["+"] / "-") "P" (dur-date / dur-time / dur-week)

            dur-date   = dur-day [dur-time]
            dur-time   = "T" (dur-hour / dur-minute / dur-second)
            dur-week   = 1*DIGIT "W"
            dur-hour   = 1*DIGIT "H" [dur-minute]
            dur-minute = 1*DIGIT "M" [dur-second]
            dur-second = 1*DIGIT "S"
            dur-day    = 1*DIGIT "D"

    Description:
        If the property permits, multiple "duration" values are
        specified by a COMMA-separated list of values.  The format is
        based on the [ISO.8601.2004] complete representation basic format
        with designators for the duration of time.  The format can
        represent nominal durations (weeks and days) and accurate
        durations (hours, minutes, and seconds).  Note that unlike
        [ISO.8601.2004], this value type doesn't support the "Y" and "M"
        designators to specify durations in terms of years and months.
        The duration of a week or a day depends on its position in the
        calendar.  In the case of discontinuities in the time scale, such
        as the change from standard time to daylight time and back, the
        computation of the exact duration requires the subtraction or
        addition of the change of duration of the discontinuity.  Leap
        seconds MUST NOT be considered when computing an exact duration.
        When computing an exact duration, the greatest order time
        components MUST be added first, that is, the number of days MUST
        be added first, followed by the number of hours, number of
        minutes, and number of seconds.

    Example:
        A duration of 15 days, 5 hours, and 20 seconds would be:

        .. code-block:: text

            P15DT5H0M20S

        A duration of 7 weeks would be:

        .. code-block:: text

            P7W

        .. code-block:: pycon

            >>> from icalendar.prop import vDuration
            >>> duration = vDuration.from_ical('P15DT5H0M20S')
            >>> duration
            datetime.timedelta(days=15, seconds=18020)
            >>> duration = vDuration.from_ical('P7W')
            >>> duration
            datetime.timedelta(days=49)
    """

    default_value: ClassVar[str] = "DURATION"
    params: Parameters

    def __init__(self, td: timedelta | str, /, params: dict[str, Any] | None = None):
        if isinstance(td, str):
            td = vDuration.from_ical(td)
        if not isinstance(td, timedelta):
            raise TypeError("Value MUST be a timedelta instance")
        self.td = td
        self.params = Parameters(params)

    def to_ical(self):
        sign = ""
        td = self.td
        if td.days < 0:
            sign = "-"
            td = -td
        timepart = ""
        if td.seconds:
            timepart = "T"
            hours = td.seconds // 3600
            minutes = td.seconds % 3600 // 60
            seconds = td.seconds % 60
            if hours:
                timepart += f"{hours}H"
            if minutes or (hours and seconds):
                timepart += f"{minutes}M"
            if seconds:
                timepart += f"{seconds}S"
        if td.days == 0 and timepart:
            return str(sign).encode("utf-8") + b"P" + str(timepart).encode("utf-8")
        return (
            str(sign).encode("utf-8")
            + b"P"
            + str(abs(td.days)).encode("utf-8")
            + b"D"
            + str(timepart).encode("utf-8")
        )

    @staticmethod
    def from_ical(ical):
        match = DURATION_REGEX.match(ical)
        if not match:
            raise InvalidCalendar(f"Invalid iCalendar duration: {ical}")

        sign, weeks, days, hours, minutes, seconds = match.groups()
        value = timedelta(
            weeks=int(weeks or 0),
            days=int(days or 0),
            hours=int(hours or 0),
            minutes=int(minutes or 0),
            seconds=int(seconds or 0),
        )

        if sign == "-":
            value = -value

        return value

    @property
    def dt(self) -> timedelta:
        """The time delta for compatibility."""
        return self.td

    @classmethod
    def examples(cls) -> list[vDuration]:
        """Examples of vDuration."""
        return [cls(timedelta(1, 99))]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [
            name,
            self.params.to_jcal(),
            self.VALUE.lower(),
            self.to_ical().decode(),
        ]

    @classmethod
    def parse_jcal_value(cls, jcal: str) -> timedelta | None:
        """Parse a jCal string to a :py:class:`datetime.timedelta`.

        Raises:
            JCalParsingError: If it can't parse a duration."""
        JCalParsingError.validate_value_type(jcal, str, cls)
        try:
            return cls.from_ical(jcal)
        except ValueError as e:
            raise JCalParsingError("Cannot parse duration.", cls, value=jcal) from e

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            duration = cls.parse_jcal_value(jcal_property[3])
        return cls(
            duration,
            Parameters.from_jcal_property(jcal_property),
        )


class vPeriod(TimeBase):
    """Period of Time

    Value Name:
        PERIOD

    Purpose:
        This value type is used to identify values that contain a
        precise period of time.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            period     = period-explicit / period-start

           period-explicit = date-time "/" date-time
           ; [ISO.8601.2004] complete representation basic format for a
           ; period of time consisting of a start and end.  The start MUST
           ; be before the end.

           period-start = date-time "/" dur-value
           ; [ISO.8601.2004] complete representation basic format for a
           ; period of time consisting of a start and positive duration
           ; of time.

    Description:
        If the property permits, multiple "period" values are
        specified by a COMMA-separated list of values.  There are two
        forms of a period of time.  First, a period of time is identified
        by its start and its end.  This format is based on the
        [ISO.8601.2004] complete representation, basic format for "DATE-
        TIME" start of the period, followed by a SOLIDUS character
        followed by the "DATE-TIME" of the end of the period.  The start
        of the period MUST be before the end of the period.  Second, a
        period of time can also be defined by a start and a positive
        duration of time.  The format is based on the [ISO.8601.2004]
        complete representation, basic format for the "DATE-TIME" start of
        the period, followed by a SOLIDUS character, followed by the
        [ISO.8601.2004] basic format for "DURATION" of the period.

    Example:
        The period starting at 18:00:00 UTC, on January 1, 1997 and
        ending at 07:00:00 UTC on January 2, 1997 would be:

        .. code-block:: text

            19970101T180000Z/19970102T070000Z

        The period start at 18:00:00 on January 1, 1997 and lasting 5 hours
        and 30 minutes would be:

        .. code-block:: text

            19970101T180000Z/PT5H30M

        .. code-block:: pycon

            >>> from icalendar.prop import vPeriod
            >>> period = vPeriod.from_ical('19970101T180000Z/19970102T070000Z')
            >>> period = vPeriod.from_ical('19970101T180000Z/PT5H30M')
    """

    default_value: ClassVar[str] = "PERIOD"
    params: Parameters
    by_duration: bool
    start: datetime
    end: datetime
    duration: timedelta

    def __init__(
        self,
        per: tuple[datetime, Union[datetime, timedelta]],
        params: dict[str, Any] | None = None,
    ):
        start, end_or_duration = per
        if not (isinstance(start, (datetime, date))):
            raise TypeError("Start value MUST be a datetime or date instance")
        if not (isinstance(end_or_duration, (datetime, date, timedelta))):
            raise TypeError(
                "end_or_duration MUST be a datetime, date or timedelta instance"
            )
        by_duration = isinstance(end_or_duration, timedelta)
        if by_duration:
            duration = end_or_duration
            end = normalize_pytz(start + duration)
        else:
            end = end_or_duration
            duration = normalize_pytz(end - start)
        if start > end:
            raise ValueError("Start time is greater than end time")

        self.params = Parameters(params or {"value": "PERIOD"})
        # set the timezone identifier
        # does not support different timezones for start and end
        self.params.update_tzid_from(start)

        self.start = start
        self.end = end
        self.by_duration = by_duration
        self.duration = duration

    def overlaps(self, other):
        if self.start > other.start:
            return other.overlaps(self)
        return self.start <= other.start < self.end

    def to_ical(self):
        if self.by_duration:
            return (
                vDatetime(self.start).to_ical()
                + b"/"
                + vDuration(self.duration).to_ical()
            )
        return vDatetime(self.start).to_ical() + b"/" + vDatetime(self.end).to_ical()

    @staticmethod
    def from_ical(ical, timezone=None):
        try:
            start, end_or_duration = ical.split("/")
            start = vDDDTypes.from_ical(start, timezone=timezone)
            end_or_duration = vDDDTypes.from_ical(end_or_duration, timezone=timezone)
        except Exception as e:
            raise ValueError(f"Expected period format, got: {ical}") from e
        return (start, end_or_duration)

    def __repr__(self):
        p = (self.start, self.duration) if self.by_duration else (self.start, self.end)
        return f"vPeriod({p!r})"

    @property
    def dt(self):
        """Make this cooperate with the other vDDDTypes."""
        return (self.start, (self.duration if self.by_duration else self.end))

    from icalendar.param import FBTYPE

    @classmethod
    def examples(cls) -> list[vPeriod]:
        """Examples of vPeriod."""
        return [
            vPeriod((datetime(2025, 11, 10, 16, 35), timedelta(hours=1, minutes=30))),  # noqa: DTZ001
            vPeriod((datetime(2025, 11, 10, 16, 35), datetime(2025, 11, 10, 18, 5))),  # noqa: DTZ001
        ]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        value = [vDatetime(self.start).to_jcal(name)[-1]]
        if self.by_duration:
            value.append(vDuration(self.duration).to_jcal(name)[-1])
        else:
            value.append(vDatetime(self.end).to_jcal(name)[-1])
        return [name, self.params.to_jcal(exclude_utc=True), self.VALUE.lower(), value]

    @classmethod
    def parse_jcal_value(
        cls, jcal: str | list
    ) -> tuple[datetime, datetime] | tuple[datetime, timedelta]:
        """Parse a jCal value.

        Raises:
            JCalParsingError: If the period is not a list with exactly two items,
                or it can't parse a date-time or duration.
        """
        if isinstance(jcal, str) and "/" in jcal:
            # only occurs in the example of RFC7265, Section B.2.2.
            jcal = jcal.split("/")
        if not isinstance(jcal, list) or len(jcal) != 2:
            raise JCalParsingError(
                "A period must be a list with exactly 2 items.", cls, value=jcal
            )
        with JCalParsingError.reraise_with_path_added(0):
            start = vDatetime.parse_jcal_value(jcal[0])
        with JCalParsingError.reraise_with_path_added(1):
            JCalParsingError.validate_value_type(jcal[1], str, cls)
            if jcal[1].startswith(("P", "-P", "+P")):
                end_or_duration = vDuration.parse_jcal_value(jcal[1])
            else:
                try:
                    end_or_duration = vDatetime.parse_jcal_value(jcal[1])
                except JCalParsingError as e:
                    raise JCalParsingError(
                        "Cannot parse date-time or duration.",
                        cls,
                        value=jcal[1],
                    ) from e
        return start, end_or_duration

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            start, end_or_duration = cls.parse_jcal_value(jcal_property[3])
        params = Parameters.from_jcal_property(jcal_property)
        tzid = params.tzid

        if tzid:
            start = tzp.localize(start, tzid)
            if is_datetime(end_or_duration):
                end_or_duration = tzp.localize(end_or_duration, tzid)

        return cls((start, end_or_duration), params=params)


class vWeekday(str):
    """Either a ``weekday`` or a ``weekdaynum``.

    .. code-block:: pycon

        >>> from icalendar import vWeekday
        >>> vWeekday("MO") # Simple weekday
        'MO'
        >>> vWeekday("2FR").relative # Second friday
        2
        >>> vWeekday("2FR").weekday
        'FR'
        >>> vWeekday("-1SU").relative # Last Sunday
        -1

    Definition from `RFC 5545, Section 3.3.10 <https://www.rfc-editor.org/rfc/rfc5545#section-3.3.10>`_:

    .. code-block:: text

        weekdaynum = [[plus / minus] ordwk] weekday
        plus        = "+"
        minus       = "-"
        ordwk       = 1*2DIGIT       ;1 to 53
        weekday     = "SU" / "MO" / "TU" / "WE" / "TH" / "FR" / "SA"
        ;Corresponding to SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY,
        ;FRIDAY, and SATURDAY days of the week.

    """

    params: Parameters
    __slots__ = ("params", "relative", "weekday")

    week_days = CaselessDict(
        {
            "SU": 0,
            "MO": 1,
            "TU": 2,
            "WE": 3,
            "TH": 4,
            "FR": 5,
            "SA": 6,
        }
    )

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        match = WEEKDAY_RULE.match(self)
        if match is None:
            raise ValueError(f"Expected weekday abbrevation, got: {self}")
        match = match.groupdict()
        sign = match["signal"]
        weekday = match["weekday"]
        relative = match["relative"]
        if weekday not in vWeekday.week_days or sign not in "+-":
            raise ValueError(f"Expected weekday abbrevation, got: {self}")
        self.weekday = weekday or None
        self.relative = (relative and int(relative)) or None
        if sign == "-" and self.relative:
            self.relative *= -1
        self.params = Parameters(params)
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING).upper()

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical.upper())
        except Exception as e:
            raise ValueError(f"Expected weekday abbrevation, got: {ical}") from e

    @classmethod
    def parse_jcal_value(cls, value: Any) -> vWeekday:
        """Parse a jCal value for vWeekday.

        Raises:
            JCalParsingError: If the value is not a valid weekday.
        """
        JCalParsingError.validate_value_type(value, str, cls)
        try:
            return cls(value)
        except ValueError as e:
            raise JCalParsingError(
                "The value must be a valid weekday.", cls, value=value
            ) from e


class vFrequency(str):
    """A simple class that catches illegal values."""

    params: Parameters
    __slots__ = ("params",)

    frequencies = CaselessDict(
        {
            "SECONDLY": "SECONDLY",
            "MINUTELY": "MINUTELY",
            "HOURLY": "HOURLY",
            "DAILY": "DAILY",
            "WEEKLY": "WEEKLY",
            "MONTHLY": "MONTHLY",
            "YEARLY": "YEARLY",
        }
    )

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        if self not in vFrequency.frequencies:
            raise ValueError(f"Expected frequency, got: {self}")
        self.params = Parameters(params)
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING).upper()

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical.upper())
        except Exception as e:
            raise ValueError(f"Expected frequency, got: {ical}") from e

    @classmethod
    def parse_jcal_value(cls, value: Any) -> vFrequency:
        """Parse a jCal value for vFrequency.

        Raises:
            JCalParsingError: If the value is not a valid frequency.
        """
        JCalParsingError.validate_value_type(value, str, cls)
        try:
            return cls(value)
        except ValueError as e:
            raise JCalParsingError(
                "The value must be a valid frequency.", cls, value=value
            ) from e


class vMonth(int):
    """The number of the month for recurrence.

    In :rfc:`5545`, this is just an int.
    In :rfc:`7529`, this can be followed by `L` to indicate a leap month.

    .. code-block:: pycon

        >>> from icalendar import vMonth
        >>> vMonth(1) # first month January
        vMonth('1')
        >>> vMonth("5L") # leap month in Hebrew calendar
        vMonth('5L')
        >>> vMonth(1).leap
        False
        >>> vMonth("5L").leap
        True

    Definition from RFC:

    .. code-block:: text

        type-bymonth = element bymonth {
           xsd:positiveInteger |
           xsd:string
        }
    """

    params: Parameters

    def __new__(cls, month: Union[str, int], /, params: dict[str, Any] | None = None):
        if isinstance(month, vMonth):
            return cls(month.to_ical().decode())
        if isinstance(month, str):
            if month.isdigit():
                month_index = int(month)
                leap = False
            else:
                if not month or (month[-1] != "L" and month[:-1].isdigit()):
                    raise ValueError(f"Invalid month: {month!r}")
                month_index = int(month[:-1])
                leap = True
        else:
            leap = False
            month_index = int(month)
        self = super().__new__(cls, month_index)
        self.leap = leap
        self.params = Parameters(params)
        return self

    def to_ical(self) -> bytes:
        """The ical representation."""
        return str(self).encode("utf-8")

    @classmethod
    def from_ical(cls, ical: str):
        return cls(ical)

    @property
    def leap(self) -> bool:
        """Whether this is a leap month."""
        return self._leap

    @leap.setter
    def leap(self, value: bool) -> None:
        self._leap = value

    def __repr__(self) -> str:
        """repr(self)"""
        return f"{self.__class__.__name__}({str(self)!r})"

    def __str__(self) -> str:
        """str(self)"""
        return f"{int(self)}{'L' if self.leap else ''}"

    @classmethod
    def parse_jcal_value(cls, value: Any) -> vMonth:
        """Parse a jCal value for vMonth.

        Raises:
            JCalParsingError: If the value is not a valid month.
        """
        JCalParsingError.validate_value_type(value, (str, int), cls)
        try:
            return cls(value)
        except ValueError as e:
            raise JCalParsingError(
                "The value must be a string or an integer.", cls, value=value
            ) from e


class vSkip(vText, Enum):
    """Skip values for RRULE.

    These are defined in :rfc:`7529`.

    OMIT  is the default value.

    Examples:

    .. code-block:: pycon

        >>> from icalendar import vSkip
        >>> vSkip.OMIT
        vSkip('OMIT')
        >>> vSkip.FORWARD
        vSkip('FORWARD')
        >>> vSkip.BACKWARD
        vSkip('BACKWARD')
    """

    OMIT = "OMIT"
    FORWARD = "FORWARD"
    BACKWARD = "BACKWARD"

    __reduce_ex__ = Enum.__reduce_ex__

    def __repr__(self):
        return f"{self.__class__.__name__}({self._name_!r})"

    @classmethod
    def parse_jcal_value(cls, value: Any) -> vSkip:
        """Parse a jCal value for vSkip.

        Raises:
            JCalParsingError: If the value is not a valid skip value.
        """
        JCalParsingError.validate_value_type(value, str, cls)
        try:
            return cls[value.upper()]
        except KeyError as e:
            raise JCalParsingError(
                "The value must be a valid skip value.", cls, value=value
            ) from e


class vRecur(CaselessDict):
    """Recurrence definition.

    Property Name:
        RRULE

    Purpose:
        This property defines a rule or repeating pattern for recurring events, to-dos,
        journal entries, or time zone definitions.

    Value Type:
        RECUR

    Property Parameters:
        IANA and non-standard property parameters can be specified on this property.

    Conformance:
        This property can be specified in recurring "VEVENT", "VTODO", and "VJOURNAL"
        calendar components as well as in the "STANDARD" and "DAYLIGHT" sub-components
        of the "VTIMEZONE" calendar component, but it SHOULD NOT be specified more than once.
        The recurrence set generated with multiple "RRULE" properties is undefined.

    Description:
        The recurrence rule, if specified, is used in computing the recurrence set.
        The recurrence set is the complete set of recurrence instances for a calendar component.
        The recurrence set is generated by considering the initial "DTSTART" property along
        with the "RRULE", "RDATE", and "EXDATE" properties contained within the
        recurring component. The "DTSTART" property defines the first instance in the
        recurrence set. The "DTSTART" property value SHOULD be synchronized with the
        recurrence rule, if specified. The recurrence set generated with a "DTSTART" property
        value not synchronized with the recurrence rule is undefined.
        The final recurrence set is generated by gathering all of the start DATE-TIME
        values generated by any of the specified "RRULE" and "RDATE" properties, and then
        excluding any start DATE-TIME values specified by "EXDATE" properties.
        This implies that start DATE- TIME values specified by "EXDATE" properties take
        precedence over those specified by inclusion properties (i.e., "RDATE" and "RRULE").
        Where duplicate instances are generated by the "RRULE" and "RDATE" properties,
        only one recurrence is considered. Duplicate instances are ignored.

        The "DTSTART" property specified within the iCalendar object defines the first
        instance of the recurrence. In most cases, a "DTSTART" property of DATE-TIME value
        type used with a recurrence rule, should be specified as a date with local time
        and time zone reference to make sure all the recurrence instances start at the
        same local time regardless of time zone changes.

        If the duration of the recurring component is specified with the "DTEND" or
        "DUE" property, then the same exact duration will apply to all the members of the
        generated recurrence set. Else, if the duration of the recurring component is
        specified with the "DURATION" property, then the same nominal duration will apply
        to all the members of the generated recurrence set and the exact duration of each
        recurrence instance will depend on its specific start time. For example, recurrence
        instances of a nominal duration of one day will have an exact duration of more or less
        than 24 hours on a day where a time zone shift occurs. The duration of a specific
        recurrence may be modified in an exception component or simply by using an
        "RDATE" property of PERIOD value type.

    Examples:
        The following RRULE specifies daily events for 10 occurrences.

        .. code-block:: text

            RRULE:FREQ=DAILY;COUNT=10

        Below, we parse the RRULE ical string.

        .. code-block:: pycon

            >>> from icalendar.prop import vRecur
            >>> rrule = vRecur.from_ical('FREQ=DAILY;COUNT=10')
            >>> rrule
            vRecur({'FREQ': ['DAILY'], 'COUNT': [10]})

        You can choose to add an rrule to an :class:`icalendar.cal.Event` or
        :class:`icalendar.cal.Todo`.

        .. code-block:: pycon

            >>> from icalendar import Event
            >>> event = Event()
            >>> event.add('RRULE', 'FREQ=DAILY;COUNT=10')
            >>> event.rrules
            [vRecur({'FREQ': ['DAILY'], 'COUNT': [10]})]
    """  # noqa: E501

    default_value: ClassVar[str] = "RECUR"
    params: Parameters

    frequencies = [
        "SECONDLY",
        "MINUTELY",
        "HOURLY",
        "DAILY",
        "WEEKLY",
        "MONTHLY",
        "YEARLY",
    ]

    # Mac iCal ignores RRULEs where FREQ is not the first rule part.
    # Sorts parts according to the order listed in RFC 5545, section 3.3.10.
    canonical_order = (
        "RSCALE",
        "FREQ",
        "UNTIL",
        "COUNT",
        "INTERVAL",
        "BYSECOND",
        "BYMINUTE",
        "BYHOUR",
        "BYDAY",
        "BYWEEKDAY",
        "BYMONTHDAY",
        "BYYEARDAY",
        "BYWEEKNO",
        "BYMONTH",
        "BYSETPOS",
        "WKST",
        "SKIP",
    )

    types = CaselessDict(
        {
            "COUNT": vInt,
            "INTERVAL": vInt,
            "BYSECOND": vInt,
            "BYMINUTE": vInt,
            "BYHOUR": vInt,
            "BYWEEKNO": vInt,
            "BYMONTHDAY": vInt,
            "BYYEARDAY": vInt,
            "BYMONTH": vMonth,
            "UNTIL": vDDDTypes,
            "BYSETPOS": vInt,
            "WKST": vWeekday,
            "BYDAY": vWeekday,
            "FREQ": vFrequency,
            "BYWEEKDAY": vWeekday,
            "SKIP": vSkip,  # RFC 7529
            "RSCALE": vText,  # RFC 7529
        }
    )

    # for reproducible serialization:
    # RULE: if and only if it can be a list it will be a list
    # look up in RFC
    jcal_not_a_list = {"FREQ", "UNTIL", "COUNT", "INTERVAL", "WKST", "SKIP", "RSCALE"}

    def __init__(self, *args, params: dict[str, Any] | None = None, **kwargs):
        if args and isinstance(args[0], str):
            # we have a string as an argument.
            args = (self.from_ical(args[0]),) + args[1:]
        for k, v in kwargs.items():
            if not isinstance(v, SEQUENCE_TYPES):
                kwargs[k] = [v]
        super().__init__(*args, **kwargs)
        self.params = Parameters(params)

    def to_ical(self):
        result = []
        for key, vals in self.sorted_items():
            typ = self.types.get(key, vText)
            if not isinstance(vals, SEQUENCE_TYPES):
                vals = [vals]  # noqa: PLW2901
            param_vals = b",".join(typ(val).to_ical() for val in vals)

            # CaselessDict keys are always unicode
            param_key = key.encode(DEFAULT_ENCODING)
            result.append(param_key + b"=" + param_vals)

        return b";".join(result)

    @classmethod
    def parse_type(cls, key, values):
        # integers
        parser = cls.types.get(key, vText)
        return [parser.from_ical(v) for v in values.split(",")]

    @classmethod
    def from_ical(cls, ical: str):
        if isinstance(ical, cls):
            return ical
        try:
            recur = cls()
            for pairs in ical.split(";"):
                try:
                    key, vals = pairs.split("=")
                except ValueError:
                    # E.g. incorrect trailing semicolon, like (issue #157):
                    # FREQ=YEARLY;BYMONTH=11;BYDAY=1SU;
                    continue
                recur[key] = cls.parse_type(key, vals)
            return cls(recur)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error in recurrence rule: {ical}") from e

    @classmethod
    def examples(cls) -> list[vRecur]:
        """Examples of vRecur."""
        return [cls.from_ical("FREQ=DAILY;COUNT=10")]

    from icalendar.param import VALUE

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        recur = {}
        for k, v in self.items():
            key = k.lower()
            if key.upper() in self.jcal_not_a_list:
                value = v[0] if isinstance(v, list) and len(v) == 1 else v
            elif not isinstance(v, list):
                value = [v]
            else:
                value = v
            recur[key] = value
        if "until" in recur:
            until = recur["until"]
            until_jcal = vDDDTypes(until).to_jcal("until")
            recur["until"] = until_jcal[-1]
        return [name, self.params.to_jcal(), self.VALUE.lower(), recur]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        params = Parameters.from_jcal_property(jcal_property)
        if not isinstance(jcal_property[3], dict) or not all(
            isinstance(k, str) for k in jcal_property[3]
        ):
            raise JCalParsingError(
                "The recurrence rule must be a mapping with string keys.",
                cls,
                3,
                value=jcal_property[3],
            )
        recur = {}
        for key, value in jcal_property[3].items():
            value_type = cls.types.get(key, vText)
            with JCalParsingError.reraise_with_path_added(3, key):
                if isinstance(value, list):
                    recur[key.lower()] = values = []
                    for i, v in enumerate(value):
                        with JCalParsingError.reraise_with_path_added(i):
                            values.append(value_type.parse_jcal_value(v))
                else:
                    recur[key] = value_type.parse_jcal_value(value)
        until = recur.get("until")
        if until is not None and not isinstance(until, list):
            recur["until"] = [until]
        return cls(recur, params=params)

    def __eq__(self, other: object) -> bool:
        """self == other"""
        if not isinstance(other, vRecur):
            return super().__eq__(other)
        if self.keys() != other.keys():
            return False
        for key in self.keys():
            v1 = self[key]
            v2 = other[key]
            if not isinstance(v1, SEQUENCE_TYPES):
                v1 = [v1]
            if not isinstance(v2, SEQUENCE_TYPES):
                v2 = [v2]
            if v1 != v2:
                return False
        return True


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
            JCalParsingError: If it can't parse a time.
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

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        with JCalParsingError.reraise_with_path_added(3):
            value = cls.parse_jcal_value(jcal_property[3])
        return cls(
            value,
            params=Parameters.from_jcal_property(jcal_property),
        )


class vUri(str):
    """URI

    Value Name:
        URI

    Purpose:
        This value type is used to identify values that contain a
        uniform resource identifier (URI) type of reference to the
        property value.

    Format Definition:
        This value type is defined by the following notation:

        .. code-block:: text

            uri = scheme ":" hier-part [ "?" query ] [ "#" fragment ]

    Description:
        This value type might be used to reference binary
        information, for values that are large, or otherwise undesirable
        to include directly in the iCalendar object.

        Property values with this value type MUST follow the generic URI
        syntax defined in [RFC3986].

        When a property parameter value is a URI value type, the URI MUST
        be specified as a quoted-string value.

    Examples:
        The following is a URI for a network file:

        .. code-block:: text

            http://example.com/my-report.txt

        .. code-block:: pycon

            >>> from icalendar.prop import vUri
            >>> uri = vUri.from_ical('http://example.com/my-report.txt')
            >>> uri
            vUri('http://example.com/my-report.txt')
            >>> uri.uri
            'http://example.com/my-report.txt'
    """

    default_value: ClassVar[str] = "URI"
    params: Parameters
    __slots__ = ("params",)

    def __new__(
        cls,
        value: str,
        encoding: str = DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.params = Parameters(params)
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical)
        except Exception as e:
            raise ValueError(f"Expected , got: {ical}") from e

    @classmethod
    def examples(cls) -> list[vUri]:
        """Examples of vUri."""
        return [cls("http://example.com/my-report.txt")]

    def to_jcal(self, name: str) -> list:
        """The jCal representation of this property according to :rfc:`7265`."""
        return [name, self.params.to_jcal(), self.VALUE.lower(), str(self)]

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        return cls(
            jcal_property[3],
            Parameters.from_jcal_property(jcal_property),
        )

    @property
    def ical_value(self) -> str:
        """The URI."""
        return self.uri

    @property
    def uri(self) -> str:
        """The URI."""
        return str(self)

    def __repr__(self) -> str:
        """repr(self)"""
        return f"{self.__class__.__name__}({self.uri!r})"

    from icalendar.param import FMTTYPE, GAP, LABEL, LANGUAGE, LINKREL, RELTYPE, VALUE


class vUid(vText):
    """A UID of a component.

    This is defined in :rfc:`9253`, Section 7.
    """

    default_value: ClassVar[str] = "UID"

    @classmethod
    def new(cls):
        """Create a new UID for convenience.

        .. code-block:: pycon

            >>> from icalendar import vUid
            >>> vUid.new()
            vUid('d755cef5-2311-46ed-a0e1-6733c9e15c63')

        """
        return vUid(uuid.uuid4())

    @property
    def uid(self) -> str:
        """The UID of this property."""
        return str(self)

    @property
    def ical_value(self) -> str:
        """The UID of this property."""
        return self.uid

    def __repr__(self) -> str:
        """repr(self)"""
        return f"{self.__class__.__name__}({self.uid!r})"

    from icalendar.param import FMTTYPE, LABEL, LINKREL

    @classmethod
    def examples(cls) -> list[vUid]:
        """Examples of vUid."""
        return [cls("d755cef5-2311-46ed-a0e1-6733c9e15c63")]


class vXmlReference(vUri):
    """An XML-REFERENCE.

    The associated value references an associated XML artifact and
    is a URI with an XPointer anchor value.

    This is defined in :rfc:`9253`, Section 7.
    """

    default_value: ClassVar[str] = "XML-REFERENCE"

    @property
    def xml_reference(self) -> str:
        """The XML reference URI of this property."""
        return self.uri

    @property
    def x_pointer(self) -> str | None:
        """The XPointer of the URI.

        The XPointer is defined in `W3C.WD-xptr-xpointer-20021219
        <https://www.rfc-editor.org/rfc/rfc9253.html#W3C.WD-xptr-xpointer-20021219>`_,
        and its use as an anchor is defined in `W3C.REC-xptr-framework-20030325
        <https://www.rfc-editor.org/rfc/rfc9253.html#W3C.REC-xptr-framework-20030325>`_.

        Returns:
            The decoded x-pointer or ``None`` if no valid x-pointer is found.
        """
        from urllib.parse import unquote, urlparse

        parsed = urlparse(self.xml_reference)
        fragment = unquote(parsed.fragment)
        if not fragment.startswith("xpointer(") or not fragment.endswith(")"):
            return None
        return fragment[9:-1]

    @classmethod
    def examples(cls) -> list[vXmlReference]:
        """Examples of vXmlReference."""
        return [cls("http://example.com/doc.xml#xpointer(/doc/element)")]


class vGeo:
    """Geographic Position

    Property Name:
        GEO

    Purpose:
        This property specifies information related to the global
        position for the activity specified by a calendar component.

    Value Type:
        FLOAT.  The value MUST be two SEMICOLON-separated FLOAT values.

    Property Parameters:
        IANA and non-standard property parameters can be specified on
        this property.

    Conformance:
        This property can be specified in "VEVENT" or "VTODO"
        calendar components.

    Description:
        This property value specifies latitude and longitude,
        in that order (i.e., "LAT LON" ordering).  The longitude
        represents the location east or west of the prime meridian as a
        positive or negative real number, respectively.  The longitude and
        latitude values MAY be specified up to six decimal places, which
        will allow for accuracy to within one meter of geographical
        position.  Receiving applications MUST accept values of this
        precision and MAY truncate values of greater precision.

        Example:

        .. code-block:: text

            GEO:37.386013;-122.082932

        Parse vGeo:

        .. code-block:: pycon

            >>> from icalendar.prop import vGeo
            >>> geo = vGeo.from_ical('37.386013;-122.082932')
            >>> geo
            (37.386013, -122.082932)

        Add a geo location to an event:

        .. code-block:: pycon

            >>> from icalendar import Event
            >>> event = Event()
            >>> latitude = 37.386013
            >>> longitude = -122.082932
            >>> event.add('GEO', (latitude, longitude))
            >>> event['GEO']
            vGeo((37.386013, -122.082932))
    """

    default_value: ClassVar[str] = "FLOAT"
    params: Parameters

    def __init__(
        self,
        geo: tuple[float | str | int, float | str | int],
        /,
        params: dict[str, Any] | None = None,
    ):
        """Create a new vGeo from a tuple of (latitude, longitude).

        Raises:
            ValueError: if geo is not a tuple of (latitude, longitude)
        """
        try:
            latitude, longitude = (geo[0], geo[1])
            latitude = float(latitude)
            longitude = float(longitude)
        except Exception as e:
            raise ValueError(
                "Input must be (float, float) for latitude and longitude"
            ) from e
        self.latitude = latitude
        self.longitude = longitude
        self.params = Parameters(params)

    def to_ical(self):
        return f"{self.latitude};{self.longitude}"

    @staticmethod
    def from_ical(ical):
        try:
            latitude, longitude = ical.split(";")
            return (float(latitude), float(longitude))
        except Exception as e:
            raise ValueError(f"Expected 'float;float' , got: {ical}") from e

    def __eq__(self, other):
        return self.to_ical() == other.to_ical()

    def __repr__(self):
        """repr(self)"""
        return f"{self.__class__.__name__}(({self.latitude}, {self.longitude}))"

    def to_jcal(self, name: str) -> list:
        """Convert to jCal object."""
        return [
            name,
            self.params.to_jcal(),
            self.VALUE.lower(),
            [self.latitude, self.longitude],
        ]

    @classmethod
    def examples(cls) -> list[vGeo]:
        """Examples of vGeo."""
        return [cls((37.386013, -122.082932))]

    from icalendar.param import VALUE

    @classmethod
    def from_jcal(cls, jcal_property: list) -> Self:
        """Parse jCal from :rfc:`7265`.

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
        """
        JCalParsingError.validate_property(jcal_property, cls)
        return cls(
            jcal_property[3],
            Parameters.from_jcal_property(jcal_property),
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

        Args:
            jcal_property: The jCal property to parse.

        Raises:
            JCalParsingError: If the provided jCal is invalid.
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


class vInline(str):
    """This is an especially dumb class that just holds raw unparsed text and
    has parameters. Conversion of inline values are handled by the Component
    class, so no further processing is needed.
    """

    params: Parameters
    __slots__ = ("params",)

    def __new__(
        cls,
        value,
        encoding=DEFAULT_ENCODING,
        /,
        params: dict[str, Any] | None = None,
    ):
        value = to_unicode(value, encoding=encoding)
        self = super().__new__(cls, value)
        self.params = Parameters(params)
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical):
        return cls(ical)


class vUnknown(vText):
    """This is text but the VALUE parameter is unknown.

    Since :rfc:`7265`, it is important to record if values are unknown.
    For :rfc:`5545`, we could just assume TEXT.
    """

    default_value: ClassVar[str] = "UNKNOWN"

    @classmethod
    def examples(cls) -> list[vUnknown]:
        """Examples of vUnknown."""
        return [vUnknown("Some property text.")]

    from icalendar.param import VALUE


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

        Args:
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


VPROPERTY: TypeAlias = Union[
    vBoolean,
    vCalAddress,
    vCategory,
    vDDDLists,
    vDDDTypes,
    vDate,
    vDatetime,
    vDuration,
    vFloat,
    vFrequency,
    vInt,
    vMonth,
    vPeriod,
    vRecur,
    vSkip,
    vText,
    vTime,
    vUTCOffset,
    vUri,
    vWeekday,
    vInline,
    vBinary,
    vGeo,
    vUnknown,
    vXmlReference,
    vUid,
]

__all__ = [
    "DURATION_REGEX",
    "VPROPERTY",
    "WEEKDAY_RULE",
    "TimeBase",
    "TypesFactory",
    "tzid_from_dt",
    "tzid_from_tzinfo",
    "vBinary",
    "vBoolean",
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
