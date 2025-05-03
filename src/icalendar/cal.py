"""Calendar is a dictionary like Python object that can render itself as VCAL
files according to RFC 5545.

These are the defined components.
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import date, datetime, timedelta, tzinfo
from typing import TYPE_CHECKING, List, NamedTuple, Optional, Tuple, Union

import dateutil.rrule
import dateutil.tz

from icalendar.attr import (
    categories_property,
    color_property,
    exdates_property,
    multi_language_text_property,
    rdates_property,
    rrules_property,
    sequence_property,
    single_int_property,
    single_string_property,
    single_utc_property,
)
from icalendar.caselessdict import CaselessDict
from icalendar.error import IncompleteComponent, InvalidCalendar
from icalendar.parser import Contentline, Contentlines, Parameters, q_join, q_split
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.prop import (
    TypesFactory,
    tzid_from_tzinfo,
    vDDDLists,
    vDDDTypes,
    vDuration,
    vText,
    vUTCOffset,
)
from icalendar.timezone import TZP, tzp
from icalendar.tools import is_date, to_datetime

if TYPE_CHECKING:
    from icalendar.alarms import Alarms


def get_example(component_directory: str, example_name: str) -> bytes:
    """Return an example and raise an error if it is absent."""
    here = os.path.dirname(__file__)
    examples = os.path.join(here, "tests", component_directory)
    if not example_name.endswith(".ics"):
        example_name = example_name + ".ics"
    example_file = os.path.join(examples, example_name)
    if not os.path.isfile(example_file):
        raise ValueError(
            f"Example {example_name} for {component_directory} not found. You can use one of {', '.join(os.listdir(examples))}"
        )
    with open(example_file, "rb") as f:
        return f.read()


######################################
# The component factory


class ComponentFactory(CaselessDict):
    """All components defined in RFC 5545 are registered in this factory class.
    To get a component you can use it like this.
    """

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict."""
        super().__init__(*args, **kwargs)
        self["VEVENT"] = Event
        self["VTODO"] = Todo
        self["VJOURNAL"] = Journal
        self["VFREEBUSY"] = FreeBusy
        self["VTIMEZONE"] = Timezone
        self["STANDARD"] = TimezoneStandard
        self["DAYLIGHT"] = TimezoneDaylight
        self["VALARM"] = Alarm
        self["VCALENDAR"] = Calendar


# These Properties have multiple property values inlined in one propertyline
# seperated by comma. Use CaselessDict as simple caseless set.
INLINE = CaselessDict(
    {
        "CATEGORIES": 1,
        "RESOURCES": 1,
        "FREEBUSY": 1,
    }
)

_marker = []


class Component(CaselessDict):
    """Component is the base object for calendar, Event and the other
    components defined in RFC 5545. Normally you will not use this class
    directly, but rather one of the subclasses.
    """

    name = None  # should be defined in each component
    required = ()  # These properties are required
    singletons = ()  # These properties must only appear once
    multiple = ()  # may occur more than once
    exclusive = ()  # These properties are mutually exclusive
    inclusive = ()  # if any occurs the other(s) MUST occur
    # ('duration', 'repeat')
    ignore_exceptions = False  # if True, and we cannot parse this
    # component, we will silently ignore
    # it, rather than let the exception
    # propagate upwards
    # not_compliant = ['']  # List of non-compliant properties.

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict."""
        super().__init__(*args, **kwargs)
        # set parameters here for properties that use non-default values
        self.subcomponents = []  # Components can be nested.
        self.errors = []  # If we ignored exception(s) while
        # parsing a property, contains error strings

    # def is_compliant(self, name):
    #    """Returns True is the given property name is compliant with the
    #    icalendar implementation.
    #
    #    If the parser is too strict it might prevent parsing erroneous but
    #    otherwise compliant properties. So the parser is pretty lax, but it is
    #    possible to test for non-compliance by calling this method.
    #    """
    #    return name in not_compliant

    def __bool__(self):
        """Returns True, CaselessDict would return False if it had no items."""
        return True

    # python 2 compatibility
    __nonzero__ = __bool__

    def is_empty(self):
        """Returns True if Component has no items or subcomponents, else False."""
        return True if not (list(self.values()) + self.subcomponents) else False  # noqa

    #############################
    # handling of property values

    @staticmethod
    def _encode(name, value, parameters=None, encode=1):
        """Encode values to icalendar property values.

        :param name: Name of the property.
        :type name: string

        :param value: Value of the property. Either of a basic Python type of
                      any of the icalendar's own property types.
        :type value: Python native type or icalendar property type.

        :param parameters: Property parameter dictionary for the value. Only
                           available, if encode is set to True.
        :type parameters: Dictionary

        :param encode: True, if the value should be encoded to one of
                       icalendar's own property types (Fallback is "vText")
                       or False, if not.
        :type encode: Boolean

        :returns: icalendar property value
        """
        if not encode:
            return value
        if isinstance(value, types_factory.all_types):
            # Don't encode already encoded values.
            obj = value
        else:
            klass = types_factory.for_property(name)
            obj = klass(value)
        if parameters:
            if not hasattr(obj, "params"):
                obj.params = Parameters()
            for key, item in parameters.items():
                if item is None:
                    if key in obj.params:
                        del obj.params[key]
                else:
                    obj.params[key] = item
        return obj

    def add(self, name, value, parameters=None, encode=1):
        """Add a property.

        :param name: Name of the property.
        :type name: string

        :param value: Value of the property. Either of a basic Python type of
                      any of the icalendar's own property types.
        :type value: Python native type or icalendar property type.

        :param parameters: Property parameter dictionary for the value. Only
                           available, if encode is set to True.
        :type parameters: Dictionary

        :param encode: True, if the value should be encoded to one of
                       icalendar's own property types (Fallback is "vText")
                       or False, if not.
        :type encode: Boolean

        :returns: None
        """
        if isinstance(value, datetime) and name.lower() in (
            "dtstamp",
            "created",
            "last-modified",
        ):
            # RFC expects UTC for those... force value conversion.
            value = tzp.localize_utc(value)

        # encode value
        if (
            encode
            and isinstance(value, list)
            and name.lower() not in ["rdate", "exdate", "categories"]
        ):
            # Individually convert each value to an ical type except rdate and
            # exdate, where lists of dates might be passed to vDDDLists.
            value = [self._encode(name, v, parameters, encode) for v in value]
        else:
            value = self._encode(name, value, parameters, encode)

        # set value
        if name in self:
            # If property already exists, append it.
            oldval = self[name]
            if isinstance(oldval, list):
                if isinstance(value, list):
                    value = oldval + value
                else:
                    oldval.append(value)
                    value = oldval
            else:
                value = [oldval, value]
        self[name] = value

    def _decode(self, name, value):
        """Internal for decoding property values."""

        # TODO: Currently the decoded method calls the icalendar.prop instances
        # from_ical. We probably want to decode properties into Python native
        # types here. But when parsing from an ical string with from_ical, we
        # want to encode the string into a real icalendar.prop property.
        if isinstance(value, vDDDLists):
            # TODO: Workaround unfinished decoding
            return value
        decoded = types_factory.from_ical(name, value)
        # TODO: remove when proper decoded is implemented in every prop.* class
        # Workaround to decode vText properly
        if isinstance(decoded, vText):
            decoded = decoded.encode(DEFAULT_ENCODING)
        return decoded

    def decoded(self, name, default=_marker):
        """Returns decoded value of property."""
        # XXX: fail. what's this function supposed to do in the end?
        # -rnix

        if name in self:
            value = self[name]
            if isinstance(value, list):
                return [self._decode(name, v) for v in value]
            return self._decode(name, value)
        else:
            if default is _marker:
                raise KeyError(name)
            else:
                return default

    ########################################################################
    # Inline values. A few properties have multiple values inlined in in one
    # property line. These methods are used for splitting and joining these.

    def get_inline(self, name, decode=1):
        """Returns a list of values (split on comma)."""
        vals = [v.strip('" ') for v in q_split(self[name])]
        if decode:
            return [self._decode(name, val) for val in vals]
        return vals

    def set_inline(self, name, values, encode=1):
        """Converts a list of values into comma separated string and sets value
        to that.
        """
        if encode:
            values = [self._encode(name, value, encode=1) for value in values]
        self[name] = types_factory["inline"](q_join(values))

    #########################
    # Handling of components

    def add_component(self, component: Component):
        """Add a subcomponent to this component."""
        self.subcomponents.append(component)

    def _walk(self, name, select):
        """Walk to given component."""
        result = []
        if (name is None or self.name == name) and select(self):
            result.append(self)
        for subcomponent in self.subcomponents:
            result += subcomponent._walk(name, select)
        return result

    def walk(self, name=None, select=lambda c: True) -> list[Component]:
        """Recursively traverses component and subcomponents. Returns sequence
        of same. If name is passed, only components with name will be returned.

        :param name: The name of the component or None such as ``VEVENT``.
        :param select: A function that takes the component as first argument
          and returns True/False.
        :returns: A list of components that match.
        :rtype: list[Component]
        """
        if name is not None:
            name = name.upper()
        return self._walk(name, select)

    #####################
    # Generation

    def property_items(self, recursive=True, sorted=True) -> list[tuple[str, object]]:
        """Returns properties in this component and subcomponents as:
        [(name, value), ...]
        """
        vText = types_factory["text"]
        properties = [("BEGIN", vText(self.name).to_ical())]
        if sorted:
            property_names = self.sorted_keys()
        else:
            property_names = self.keys()

        for name in property_names:
            values = self[name]
            if isinstance(values, list):
                # normally one property is one line
                for value in values:
                    properties.append((name, value))
            else:
                properties.append((name, values))
        if recursive:
            # recursion is fun!
            for subcomponent in self.subcomponents:
                properties += subcomponent.property_items(sorted=sorted)
        properties.append(("END", vText(self.name).to_ical()))
        return properties

    @classmethod
    def from_ical(cls, st, multiple=False):
        """Populates the component recursively from a string."""
        stack = []  # a stack of components
        comps = []
        for line in Contentlines.from_ical(st):  # raw parsing
            if not line:
                continue

            try:
                name, params, vals = line.parts()
            except ValueError as e:
                # if unable to parse a line within a component
                # that ignores exceptions, mark the component
                # as broken and skip the line. otherwise raise.
                component = stack[-1] if stack else None
                if not component or not component.ignore_exceptions:
                    raise
                component.errors.append((None, str(e)))
                continue

            uname = name.upper()
            # check for start of component
            if uname == "BEGIN":
                # try and create one of the components defined in the spec,
                # otherwise get a general Components for robustness.
                c_name = vals.upper()
                c_class = component_factory.get(c_name, Component)
                # If component factory cannot resolve ``c_name``, the generic
                # ``Component`` class is used which does not have the name set.
                # That's opposed to the usage of ``cls``, which represents a
                # more concrete subclass with a name set (e.g. VCALENDAR).
                component = c_class()
                if not getattr(component, "name", ""):  # undefined components
                    component.name = c_name
                stack.append(component)
            # check for end of event
            elif uname == "END":
                # we are done adding properties to this component
                # so pop it from the stack and add it to the new top.
                if not stack:
                    # The stack is currently empty, the input must be invalid
                    raise ValueError("END encountered without an accompanying BEGIN!")

                component = stack.pop()
                if not stack:  # we are at the end
                    comps.append(component)
                else:
                    stack[-1].add_component(component)
                if vals == "VTIMEZONE" and "TZID" in component:
                    tzp.cache_timezone_component(component)
            # we are adding properties to the current top of the stack
            else:
                factory = types_factory.for_property(name)
                component = stack[-1] if stack else None
                if not component:
                    # only accept X-COMMENT at the end of the .ics file
                    # ignore these components in parsing
                    if uname == "X-COMMENT":
                        break
                    else:
                        raise ValueError(
                            f'Property "{name}" does not have a parent component.'
                        )
                datetime_names = (
                    "DTSTART",
                    "DTEND",
                    "RECURRENCE-ID",
                    "DUE",
                    "RDATE",
                    "EXDATE",
                )
                try:
                    if name == "FREEBUSY":
                        vals = vals.split(",")
                        if "TZID" in params:
                            parsed_components = [
                                factory(factory.from_ical(val, params["TZID"]))
                                for val in vals
                            ]
                        else:
                            parsed_components = [
                                factory(factory.from_ical(val)) for val in vals
                            ]
                    elif name in datetime_names and "TZID" in params:
                        parsed_components = [
                            factory(factory.from_ical(vals, params["TZID"]))
                        ]
                    else:
                        parsed_components = [factory(factory.from_ical(vals))]
                except ValueError as e:
                    if not component.ignore_exceptions:
                        raise
                    component.errors.append((uname, str(e)))
                else:
                    for parsed_component in parsed_components:
                        parsed_component.params = params
                        component.add(name, parsed_component, encode=0)

        if multiple:
            return comps
        if len(comps) > 1:
            raise ValueError(
                cls._format_error(
                    "Found multiple components where only one is allowed", st
                )
            )
        if len(comps) < 1:
            raise ValueError(
                cls._format_error(
                    "Found no components where exactly one is required", st
                )
            )
        return comps[0]

    @staticmethod
    def _format_error(error_description, bad_input, elipsis="[...]"):
        # there's three character more in the error, ie. ' ' x2 and a ':'
        max_error_length = 100 - 3
        if len(error_description) + len(bad_input) + len(elipsis) > max_error_length:
            truncate_to = max_error_length - len(error_description) - len(elipsis)
            return f"{error_description}: {bad_input[:truncate_to]} {elipsis}"
        else:
            return f"{error_description}: {bad_input}"

    def content_line(self, name, value, sorted=True):
        """Returns property as content line."""
        params = getattr(value, "params", Parameters())
        return Contentline.from_parts(name, params, value, sorted=sorted)

    def content_lines(self, sorted=True):
        """Converts the Component and subcomponents into content lines."""
        contentlines = Contentlines()
        for name, value in self.property_items(sorted=sorted):
            cl = self.content_line(name, value, sorted=sorted)
            contentlines.append(cl)
        contentlines.append("")  # remember the empty string in the end
        return contentlines

    def to_ical(self, sorted=True):
        """
        :param sorted: Whether parameters and properties should be
                       lexicographically sorted.
        """

        content_lines = self.content_lines(sorted=sorted)
        return content_lines.to_ical()

    def __repr__(self):
        """String representation of class with all of it's subcomponents."""
        subs = ", ".join(str(it) for it in self.subcomponents)
        return f"{self.name or type(self).__name__}({dict(self)}{', ' + subs if subs else ''})"

    def __eq__(self, other):
        if len(self.subcomponents) != len(other.subcomponents):
            return False

        properties_equal = super().__eq__(other)
        if not properties_equal:
            return False

        # The subcomponents might not be in the same order,
        # neither there's a natural key we can sort the subcomponents by nor
        # are the subcomponent types hashable, so  we cant put them in a set to
        # check for set equivalence. We have to iterate over the subcomponents
        # and look for each of them in the list.
        for subcomponent in self.subcomponents:
            if subcomponent not in other.subcomponents:
                return False

        return True

    DTSTAMP = single_utc_property(
        "DTSTAMP",
        """RFC 5545:

        Conformance:  This property MUST be included in the "VEVENT",
        "VTODO", "VJOURNAL", or "VFREEBUSY" calendar components.

        Description: In the case of an iCalendar object that specifies a
        "METHOD" property, this property specifies the date and time that
        the instance of the iCalendar object was created.  In the case of
        an iCalendar object that doesn't specify a "METHOD" property, this
        property specifies the date and time that the information
        associated with the calendar component was last revised in the
        calendar store.

        The value MUST be specified in the UTC time format.

        In the case of an iCalendar object that doesn't specify a "METHOD"
        property, this property is equivalent to the "LAST-MODIFIED"
        property.
    """,
    )
    LAST_MODIFIED = single_utc_property(
        "LAST-MODIFIED",
        """RFC 5545:

        Purpose:  This property specifies the date and time that the
        information associated with the calendar component was last
        revised in the calendar store.

        Note: This is analogous to the modification date and time for a
        file in the file system.

        Conformance:  This property can be specified in the "VEVENT",
        "VTODO", "VJOURNAL", or "VTIMEZONE" calendar components.
    """,
    )

    def is_thunderbird(self) -> bool:
        """Whether this component has attributes that indicate that Mozilla Thunderbird created it."""
        return any(attr.startswith("X-MOZ-") for attr in self.keys())


#######################################
# components defined in RFC 5545


def create_single_property(
    prop: str,
    value_attr: Optional[str],
    value_type: tuple[type],
    type_def: type,
    doc: str,
    vProp: type = vDDDTypes,  # noqa: N803
):
    """Create a single property getter and setter.

    :param prop: The name of the property.
    :param value_attr: The name of the attribute to get the value from.
    :param value_type: The type of the value.
    :param type_def: The type of the property.
    :param doc: The docstring of the property.
    :param vProp: The type of the property from :mod:`icalendar.prop`.
    """

    def p_get(self: Component):
        default = object()
        result = self.get(prop, default)
        if result is default:
            return None
        if isinstance(result, list):
            raise InvalidCalendar(f"Multiple {prop} defined.")
        value = result if value_attr is None else getattr(result, value_attr, result)
        if not isinstance(value, value_type):
            raise InvalidCalendar(
                f"{prop} must be either a {' or '.join(t.__name__ for t in value_type)}, not {value}."
            )
        return value

    def p_set(self: Component, value) -> None:
        if value is None:
            p_del(self)
            return
        if not isinstance(value, value_type):
            raise TypeError(
                f"Use {' or '.join(t.__name__ for t in value_type)}, not {type(value).__name__}."
            )
        self[prop] = vProp(value)
        if prop in self.exclusive:
            for other_prop in self.exclusive:
                if other_prop != prop:
                    self.pop(other_prop, None)

    p_set.__annotations__["value"] = p_get.__annotations__["return"] = Optional[
        type_def
    ]

    def p_del(self: Component):
        self.pop(prop)

    p_doc = f"""The {prop} property.

    {doc}

    Accepted values: {', '.join(t.__name__ for t in value_type)}.
    If the attribute has invalid values, we raise InvalidCalendar.
    If the value is absent, we return None.
    You can also delete the value with del or by setting it to None.
    """
    return property(p_get, p_set, p_del, p_doc)


_X_MOZ_SNOOZE_TIME = single_utc_property(
    "X-MOZ-SNOOZE-TIME", "Thunderbird: Alarms before this time are snoozed."
)
_X_MOZ_LASTACK = single_utc_property(
    "X-MOZ-LASTACK", "Thunderbird: Alarms before this time are acknowledged."
)


def _get_duration(self: Component) -> Optional[timedelta]:
    """Getter for property DURATION."""
    default = object()
    duration = self.get("duration", default)
    if isinstance(duration, vDDDTypes):
        return duration.dt
    if isinstance(duration, vDuration):
        return duration.td
    if duration is not default and not isinstance(duration, timedelta):
        raise InvalidCalendar(
            f"DURATION must be a timedelta, not {type(duration).__name__}."
        )
    return None


def _set_duration(self: Component, value: Optional[timedelta]):
    """Setter for property DURATION."""
    if value is None:
        self.pop("duration", None)
        return
    if not isinstance(value, timedelta):
        raise TypeError(f"Use timedelta, not {type(value).__name__}.")
    self["duration"] = vDuration(value)
    self.pop("DTEND")
    self.pop("DUE")


def _del_duration(self: Component):
    """Delete property DURATION."""
    self.pop("DURATION")


_doc_duration = """The DURATION property.

The "DTSTART" property for a "{component}" specifies the inclusive start of the event.
The "DURATION" property in conjunction with the DTSTART property
for a "{component}" calendar component specifies the non-inclusive end
of the event.

If you would like to calculate the duration of a {component}, do not use this.
Instead use the duration property (lower case).
"""


class Event(Component):
    """
    A "VEVENT" calendar component is a grouping of component
    properties that represents a scheduled amount of time on a
    calendar. For example, it can be an activity, such as a one-hour
    long department meeting from 8:00 AM to 9:00 AM, tomorrow.
    """

    name = "VEVENT"

    canonical_order = (
        "SUMMARY",
        "DTSTART",
        "DTEND",
        "DURATION",
        "DTSTAMP",
        "UID",
        "RECURRENCE-ID",
        "SEQUENCE",
        "RRULE",
        "RDATE",
        "EXDATE",
    )

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CLASS",
        "CREATED",
        "COLOR",
        "DESCRIPTION",
        "DTSTART",
        "GEO",
        "LAST-MODIFIED",
        "LOCATION",
        "ORGANIZER",
        "PRIORITY",
        "DTSTAMP",
        "SEQUENCE",
        "STATUS",
        "SUMMARY",
        "TRANSP",
        "URL",
        "RECURRENCE-ID",
        "DTEND",
        "DURATION",
        "UID",
    )
    exclusive = (
        "DTEND",
        "DURATION",
    )
    multiple = (
        "ATTACH",
        "ATTENDEE",
        "CATEGORIES",
        "COMMENT",
        "CONTACT",
        "EXDATE",
        "RSTATUS",
        "RELATED",
        "RESOURCES",
        "RDATE",
        "RRULE",
    )
    ignore_exceptions = True

    @property
    def alarms(self) -> Alarms:
        """Compute the alarm times for this component.

        >>> from icalendar import Event
        >>> event = Event.example("rfc_9074_example_1")
        >>> len(event.alarms.times)
        1
        >>> alarm_time = event.alarms.times[0]
        >>> alarm_time.trigger  # The time when the alarm pops up
        datetime.datetime(2021, 3, 2, 10, 15, tzinfo=ZoneInfo(key='America/New_York'))
        >>> alarm_time.is_active()  # This alarm has not been acknowledged
        True

        Note that this only uses DTSTART and DTEND, but ignores
        RDATE, EXDATE, and RRULE properties.
        """
        from icalendar.alarms import Alarms

        return Alarms(self)

    @classmethod
    def example(cls, name: str = "rfc_9074_example_3") -> Event:
        """Return the calendar example with the given name."""
        return cls.from_ical(get_example("events", name))

    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VEVENT" specifies the inclusive start of the event.',
    )
    DTEND = create_single_property(
        "DTEND",
        "dt",
        (datetime, date),
        date,
        'The "DTEND" property for a "VEVENT" calendar component specifies the non-inclusive end of the event.',
    )

    def _get_start_end_duration(self):
        """Verify the calendar validity and return the right attributes."""
        start = self.DTSTART
        end = self.DTEND
        duration = self.DURATION
        if duration is not None and end is not None:
            raise InvalidCalendar(
                "Only one of DTEND and DURATION may be in a VEVENT, not both."
            )
        if (
            isinstance(start, date)
            and not isinstance(start, datetime)
            and duration is not None
            and duration.seconds != 0
        ):
            raise InvalidCalendar(
                "When DTSTART is a date, DURATION must be of days or weeks."
            )
        if start is not None and end is not None and is_date(start) != is_date(end):
            raise InvalidCalendar(
                "DTSTART and DTEND must be of the same type, either date or datetime."
            )
        return start, end, duration

    DURATION = property(
        _get_duration,
        _set_duration,
        _del_duration,
        _doc_duration.format(component="VEVENT"),
    )

    @property
    def duration(self) -> timedelta:
        """The duration of the VEVENT.

        This duration is calculated from the start and end of the event.
        You cannot set the duration as it is unclear what happens to start and end.
        """
        return self.end - self.start

    @property
    def start(self) -> date | datetime:
        """The start of the component.

        Invalid values raise an InvalidCalendar.
        If there is no start, we also raise an IncompleteComponent error.

        You can get the start, end and duration of an event as follows:

        >>> from datetime import datetime
        >>> from icalendar import Event
        >>> event = Event()
        >>> event.start = datetime(2021, 1, 1, 12)
        >>> event.end = datetime(2021, 1, 1, 12, 30) # 30 minutes
        >>> event.duration  # 1800 seconds == 30 minutes
        datetime.timedelta(seconds=1800)
        >>> print(event.to_ical())
        BEGIN:VEVENT
        DTSTART:20210101T120000
        DTEND:20210101T123000
        END:VEVENT
        """
        start = self._get_start_end_duration()[0]
        if start is None:
            raise IncompleteComponent("No DTSTART given.")
        return start

    @start.setter
    def start(self, start: Optional[date | datetime]):
        """Set the start."""
        self.DTSTART = start

    @property
    def end(self) -> date | datetime:
        """The end of the component.

        Invalid values raise an InvalidCalendar error.
        If there is no end, we also raise an IncompleteComponent error.
        """
        start, end, duration = self._get_start_end_duration()
        if end is None and duration is None:
            if start is None:
                raise IncompleteComponent("No DTEND or DURATION+DTSTART given.")
            if is_date(start):
                return start + timedelta(days=1)
            return start
        if duration is not None:
            if start is not None:
                return start + duration
            raise IncompleteComponent("No DTEND or DURATION+DTSTART given.")
        return end

    @end.setter
    def end(self, end: date | datetime | None):
        """Set the end."""
        self.DTEND = end

    X_MOZ_SNOOZE_TIME = _X_MOZ_SNOOZE_TIME
    X_MOZ_LASTACK = _X_MOZ_LASTACK
    color = color_property
    sequence = sequence_property
    categories = categories_property
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property


class Todo(Component):
    """
    A "VTODO" calendar component is a grouping of component
    properties that represents an action item or assignment. For
    example, it can be used to represent an item of work assigned to
    an individual, such as "Prepare for the upcoming conference
    seminar on Internet Calendaring".
    """

    name = "VTODO"

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CLASS",
        "COLOR",
        "COMPLETED",
        "CREATED",
        "DESCRIPTION",
        "DTSTAMP",
        "DTSTART",
        "GEO",
        "LAST-MODIFIED",
        "LOCATION",
        "ORGANIZER",
        "PERCENT-COMPLETE",
        "PRIORITY",
        "RECURRENCE-ID",
        "SEQUENCE",
        "STATUS",
        "SUMMARY",
        "UID",
        "URL",
        "DUE",
        "DURATION",
    )
    exclusive = (
        "DUE",
        "DURATION",
    )
    multiple = (
        "ATTACH",
        "ATTENDEE",
        "CATEGORIES",
        "COMMENT",
        "CONTACT",
        "EXDATE",
        "RSTATUS",
        "RELATED",
        "RESOURCES",
        "RDATE",
        "RRULE",
    )
    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VTODO" specifies the inclusive start of the Todo.',
    )
    DUE = create_single_property(
        "DUE",
        "dt",
        (datetime, date),
        date,
        'The "DUE" property for a "VTODO" calendar component specifies the non-inclusive end of the Todo.',
    )
    DURATION = property(
        _get_duration,
        _set_duration,
        _del_duration,
        _doc_duration.format(component="VTODO"),
    )

    def _get_start_end_duration(self):
        """Verify the calendar validity and return the right attributes."""
        start = self.DTSTART
        end = self.DUE
        duration = self.DURATION
        if duration is not None and end is not None:
            raise InvalidCalendar(
                "Only one of DUE and DURATION may be in a VTODO, not both."
            )
        if (
            isinstance(start, date)
            and not isinstance(start, datetime)
            and duration is not None
            and duration.seconds != 0
        ):
            raise InvalidCalendar(
                "When DTSTART is a date, DURATION must be of days or weeks."
            )
        if start is not None and end is not None and is_date(start) != is_date(end):
            raise InvalidCalendar(
                "DTSTART and DUE must be of the same type, either date or datetime."
            )
        return start, end, duration

    @property
    def start(self) -> date | datetime:
        """The start of the VTODO.

        Invalid values raise an InvalidCalendar.
        If there is no start, we also raise an IncompleteComponent error.

        You can get the start, end and duration of a Todo as follows:

        >>> from datetime import datetime
        >>> from icalendar import Todo
        >>> todo = Todo()
        >>> todo.start = datetime(2021, 1, 1, 12)
        >>> todo.end = datetime(2021, 1, 1, 12, 30) # 30 minutes
        >>> todo.duration  # 1800 seconds == 30 minutes
        datetime.timedelta(seconds=1800)
        >>> print(todo.to_ical())
        BEGIN:VTODO
        DTSTART:20210101T120000
        DUE:20210101T123000
        END:VTODO
        """
        start = self._get_start_end_duration()[0]
        if start is None:
            raise IncompleteComponent("No DTSTART given.")
        return start

    @start.setter
    def start(self, start: Optional[date | datetime]):
        """Set the start."""
        self.DTSTART = start

    @property
    def end(self) -> date | datetime:
        """The end of the component.

        Invalid values raise an InvalidCalendar error.
        If there is no end, we also raise an IncompleteComponent error.
        """
        start, end, duration = self._get_start_end_duration()
        if end is None and duration is None:
            if start is None:
                raise IncompleteComponent("No DUE or DURATION+DTSTART given.")
            if is_date(start):
                return start + timedelta(days=1)
            return start
        if duration is not None:
            if start is not None:
                return start + duration
            raise IncompleteComponent("No DUE or DURATION+DTSTART given.")
        return end

    @end.setter
    def end(self, end: date | datetime | None):
        """Set the end."""
        self.DUE = end

    @property
    def duration(self) -> timedelta:
        """The duration of the VTODO.

        This duration is calculated from the start and end of the Todo.
        You cannot set the duration as it is unclear what happens to start and end.
        """
        return self.end - self.start

    X_MOZ_SNOOZE_TIME = _X_MOZ_SNOOZE_TIME
    X_MOZ_LASTACK = _X_MOZ_LASTACK

    @property
    def alarms(self) -> Alarms:
        """Compute the alarm times for this component.

        >>> from datetime import datetime
        >>> from icalendar import Todo
        >>> todo = Todo()  # empty without alarms
        >>> todo.start = datetime(2024, 10, 26, 10, 21)
        >>> len(todo.alarms.times)
        0

        Note that this only uses DTSTART and DUE, but ignores
        RDATE, EXDATE, and RRULE properties.
        """
        from icalendar.alarms import Alarms

        return Alarms(self)

    color = color_property
    sequence = sequence_property
    categories = categories_property
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property


class Journal(Component):
    """A descriptive text at a certain time or associated with a component.

    A "VJOURNAL" calendar component is a grouping of
    component properties that represent one or more descriptive text
    notes associated with a particular calendar date.  The "DTSTART"
    property is used to specify the calendar date with which the
    journal entry is associated.  Generally, it will have a DATE value
    data type, but it can also be used to specify a DATE-TIME value
    data type.  Examples of a journal entry include a daily record of
    a legislative body or a journal entry of individual telephone
    contacts for the day or an ordered list of accomplishments for the
    day.
    """

    name = "VJOURNAL"

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CLASS",
        "COLOR",
        "CREATED",
        "DTSTART",
        "DTSTAMP",
        "LAST-MODIFIED",
        "ORGANIZER",
        "RECURRENCE-ID",
        "SEQUENCE",
        "STATUS",
        "SUMMARY",
        "UID",
        "URL",
    )
    multiple = (
        "ATTACH",
        "ATTENDEE",
        "CATEGORIES",
        "COMMENT",
        "CONTACT",
        "EXDATE",
        "RELATED",
        "RDATE",
        "RRULE",
        "RSTATUS",
        "DESCRIPTION",
    )

    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime, date),
        date,
        'The "DTSTART" property for a "VJOURNAL" that specifies the exact date at which the journal entry was made.',
    )

    @property
    def start(self) -> date:
        """The start of the Journal.

        The "DTSTART"
        property is used to specify the calendar date with which the
        journal entry is associated.
        """
        start = self.DTSTART
        if start is None:
            raise IncompleteComponent("No DTSTART given.")
        return start

    @start.setter
    def start(self, value: datetime | date) -> None:
        """Set the start of the journal."""
        self.DTSTART = value

    end = start

    @property
    def duration(self) -> timedelta:
        """The journal has no duration: timedelta(0)."""
        return timedelta(0)

    color = color_property
    sequence = sequence_property
    categories = categories_property
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property


class FreeBusy(Component):
    """
    A "VFREEBUSY" calendar component is a grouping of component
    properties that represents either a request for free or busy time
    information, a reply to a request for free or busy time
    information, or a published set of busy time information.
    """

    name = "VFREEBUSY"

    required = (
        "UID",
        "DTSTAMP",
    )
    singletons = (
        "CONTACT",
        "DTSTART",
        "DTEND",
        "DTSTAMP",
        "ORGANIZER",
        "UID",
        "URL",
    )
    multiple = (
        "ATTENDEE",
        "COMMENT",
        "FREEBUSY",
        "RSTATUS",
    )


class Timezone(Component):
    """
    A "VTIMEZONE" calendar component is a grouping of component
    properties that defines a time zone. It is used to describe the
    way in which a time zone changes its offset from UTC over time.
    """

    subcomponents: list[TimezoneStandard|TimezoneDaylight]

    name = "VTIMEZONE"
    canonical_order = ("TZID",)
    required = ("TZID",)  # it also requires one of components DAYLIGHT and STANDARD
    singletons = (
        "TZID",
        "LAST-MODIFIED",
        "TZURL",
    )

    _DEFAULT_FIRST_DATE = date(1970, 1, 1)
    _DEFAULT_LAST_DATE = date(2038, 1, 1)

    @classmethod
    def example(cls, name: str = "pacific_fiji") -> Calendar:
        """Return the timezone example with the given name."""
        return cls.from_ical(get_example("timezones", name))

    @staticmethod
    def _extract_offsets(component: TimezoneDaylight | TimezoneStandard, tzname: str):
        """extract offsets and transition times from a VTIMEZONE component
        :param component: a STANDARD or DAYLIGHT component
        :param tzname: the name of the zone
        """
        offsetfrom = component.TZOFFSETFROM
        offsetto = component.TZOFFSETTO
        dtstart = component.DTSTART

        # offsets need to be rounded to the next minute, we might loose up
        # to 30 seconds accuracy, but it can't be helped (datetime
        # supposedly cannot handle smaller offsets)
        offsetto_s = int((offsetto.seconds + 30) / 60) * 60
        offsetto = timedelta(days=offsetto.days, seconds=offsetto_s)
        offsetfrom_s = int((offsetfrom.seconds + 30) / 60) * 60
        offsetfrom = timedelta(days=offsetfrom.days, seconds=offsetfrom_s)

        # expand recurrences
        if "RRULE" in component:
            # to be paranoid about correct weekdays
            # evaluate the rrule with the current offset
            tzi = dateutil.tz.tzoffset("(offsetfrom)", offsetfrom)
            rrstart = dtstart.replace(tzinfo=tzi)

            rrulestr = component["RRULE"].to_ical().decode("utf-8")
            rrule = dateutil.rrule.rrulestr(rrulestr, dtstart=rrstart)
            tzp.fix_rrule_until(rrule, component["RRULE"])

            # constructing the timezone requires UTC transition times.
            # here we construct local times without tzinfo, the offset to UTC
            # gets subtracted in to_tz().
            transtimes = [dt.replace(tzinfo=None) for dt in rrule]

        # or rdates
        elif "RDATE" in component:
            if not isinstance(component["RDATE"], list):
                rdates = [component["RDATE"]]
            else:
                rdates = component["RDATE"]
            transtimes = [dtstart] + [leaf.dt for tree in rdates for leaf in tree.dts]
        else:
            transtimes = [dtstart]

        transitions = [
            (transtime, offsetfrom, offsetto, tzname) for transtime in set(transtimes)
        ]

        if component.name == "STANDARD":
            is_dst = 0
        elif component.name == "DAYLIGHT":
            is_dst = 1
        return is_dst, transitions

    @staticmethod
    def _make_unique_tzname(tzname, tznames):
        """
        :param tzname: Candidate tzname
        :param tznames: Other tznames
        """
        # TODO better way of making sure tznames are unique
        while tzname in tznames:
            tzname += "_1"
        tznames.add(tzname)
        return tzname

    def to_tz(self, tzp: TZP = tzp, lookup_tzid: bool = True):
        """convert this VTIMEZONE component to a timezone object

        :param tzp: timezone provider to use
        :param lookup_tzid: whether to use the TZID property to look up existing
                            timezone definitions with tzp.
                            If it is False, a new timezone will be created.
                            If it is True, the existing timezone will be used
                            if it exists, otherwise a new timezone will be created.
        """
        if lookup_tzid:
            tz = tzp.timezone(self.tz_name)
            if tz is not None:
                return tz
        return tzp.create_timezone(self)

    @property
    def tz_name(self) -> str:
        """Return the name of the timezone component.

        Please note that the names of the timezone are different from this name
        and may change with winter/summer time.
        """
        try:
            return str(self["TZID"])
        except UnicodeEncodeError:
            return self["TZID"].encode("ascii", "replace")

    def get_transitions(
        self,
    ) -> Tuple[List[datetime], List[Tuple[timedelta, timedelta, str]]]:
        """Return a tuple of (transition_times, transition_info)

        - transition_times = [datetime, ...]
        - transition_info = [(TZOFFSETTO, dts_offset, tzname)]

        """
        zone = self.tz_name
        transitions = []
        dst = {}
        tznames = set()
        for component in self.walk():
            if type(component) == Timezone:
                continue
            if is_date(component["DTSTART"].dt):
                component.DTSTART = to_datetime(component["DTSTART"].dt)
            assert isinstance(
                component["DTSTART"].dt, datetime
            ), "VTIMEZONEs sub-components' DTSTART must be of type datetime, not date"
            try:
                tzname = str(component["TZNAME"])
            except UnicodeEncodeError:
                tzname = component["TZNAME"].encode("ascii", "replace")
                tzname = self._make_unique_tzname(tzname, tznames)
            except KeyError:
                # for whatever reason this is str/unicode
                tzname = (
                    f"{zone}_{component['DTSTART'].to_ical().decode('utf-8')}_"
                    + f"{component['TZOFFSETFROM'].to_ical()}_"
                    + f"{component['TZOFFSETTO'].to_ical()}"
                )
                tzname = self._make_unique_tzname(tzname, tznames)

            dst[tzname], component_transitions = self._extract_offsets(
                component, tzname
            )
            transitions.extend(component_transitions)

        transitions.sort()
        transition_times = [
            transtime - osfrom for transtime, osfrom, _, _ in transitions
        ]

        # transition_info is a list with tuples in the format
        # (utcoffset, dstoffset, name)
        # dstoffset = 0, if current transition is to standard time
        #           = this_utcoffset - prev_standard_utcoffset, otherwise
        transition_info = []
        for num, (transtime, osfrom, osto, name) in enumerate(transitions):
            dst_offset = False
            if not dst[name]:
                dst_offset = timedelta(seconds=0)
            else:
                # go back in time until we find a transition to dst
                for index in range(num - 1, -1, -1):
                    if not dst[transitions[index][3]]:  # [3] is the name
                        dst_offset = osto - transitions[index][2]  # [2] is osto  # noqa
                        break
                # when the first transition is to dst, we didn't find anything
                # in the past, so we have to look into the future
                if not dst_offset:
                    for index in range(num, len(transitions)):
                        if not dst[transitions[index][3]]:  # [3] is the name
                            dst_offset = (
                                osto - transitions[index][2]
                            )  # [2] is osto  # noqa
                            break
            assert dst_offset is not False
            transition_info.append((osto, dst_offset, name))
        return transition_times, transition_info

    # binary search
    _from_tzinfo_skip_search = [
        timedelta(days=days) for days in (64, 32, 16, 8, 4, 2, 1)
    ] + [
        # we know it happens in the night usually around 1am
        timedelta(hours=4),
        timedelta(hours=1),
        # adding some minutes and seconds for faster search
        timedelta(minutes=20),
        timedelta(minutes=5),
        timedelta(minutes=1),
        timedelta(seconds=20),
        timedelta(seconds=5),
        timedelta(seconds=1),
    ]

    @classmethod
    def from_tzinfo(
        cls,
        timezone: tzinfo,
        tzid: Optional[str] = None,
        first_date: date = _DEFAULT_FIRST_DATE,
        last_date: date = _DEFAULT_LAST_DATE,
    ) -> Timezone:
        """Return a VTIMEZONE component from a timezone object.

        This works with pytz and zoneinfo and any other timezone.
        The offsets are calculated from the tzinfo object.

        Parameters:

        :param tzinfo: the timezone object
        :param tzid: the tzid for this timezone. If None, it will be extracted from the tzinfo.
        :param first_date: a datetime that is earlier than anything that happens in the calendar
        :param last_date: a datetime that is later than anything that happens in the calendar
        :raises ValueError: If we have no tzid and cannot extract one.

        .. note::
            This can take some time. Please cache the results.
        """
        if tzid is None:
            tzid = tzid_from_tzinfo(timezone)
            if tzid is None:
                raise ValueError(
                    f"Cannot get TZID from {timezone}. Please set the tzid parameter."
                )
        normalize = getattr(timezone, "normalize", lambda dt: dt)  # pytz compatibility
        first_datetime = datetime(first_date.year, first_date.month, first_date.day)  # noqa: DTZ001
        last_datetime = datetime(last_date.year, last_date.month, last_date.day)  # noqa: DTZ001
        if hasattr(timezone, "localize"):  # pytz compatibility
            first_datetime = timezone.localize(first_datetime)
            last_datetime = timezone.localize(last_datetime)
        else:
            first_datetime = first_datetime.replace(tzinfo=timezone)
            last_datetime = last_datetime.replace(tzinfo=timezone)
        # from, to, tzname, is_standard -> start
        offsets: dict[
            tuple[Optional[timedelta], timedelta, str, bool], list[datetime]
        ] = defaultdict(list)
        start = first_datetime
        offset_to = None
        while start < last_datetime:
            offset_from = offset_to
            end = start
            offset_to = end.utcoffset()
            for add_offset in cls._from_tzinfo_skip_search:
                last_end = end  # we need to save this as we might be left and right of the time change
                end = normalize(end + add_offset)
                try:
                    while end.utcoffset() == offset_to:
                        last_end = end
                        end = normalize(end + add_offset)
                except OverflowError:
                    # zoninfo does not go all the way
                    break
                # retract if we overshoot
                end = last_end
            # Now, start (inclusive) -> end (exclusive) are one timezone
            is_standard = start.dst() == timedelta()
            name = start.tzname()
            if name is None:
                name = str(offset_to)
            key = (offset_from, offset_to, name, is_standard)
            # first_key = (None,) + key[1:]
            # if first_key in offsets:
            #     # remove the first one and claim it changes at that day
            #     offsets[first_key] = offsets.pop(first_key)
            offsets[key].append(start.replace(tzinfo=None))
            start = normalize(end + cls._from_tzinfo_skip_search[-1])
        tz = cls()
        tz.add("TZID", tzid)
        tz.add("COMMENT", f"This timezone only works from {first_date} to {last_date}.")
        for (offset_from, offset_to, tzname, is_standard), starts in offsets.items():
            first_start = min(starts)
            starts.remove(first_start)
            if first_start.date() == last_date:
                first_start = datetime(last_date.year, last_date.month, last_date.day)  # noqa: DTZ001
            subcomponent = TimezoneStandard() if is_standard else TimezoneDaylight()
            if offset_from is None:
                offset_from = offset_to  # noqa: PLW2901
            subcomponent.TZOFFSETFROM = offset_from
            subcomponent.TZOFFSETTO = offset_to
            subcomponent.add("TZNAME", tzname)
            subcomponent.DTSTART = first_start
            if starts:
                subcomponent.add("RDATE", starts)
            tz.add_component(subcomponent)
        return tz

    @classmethod
    def from_tzid(
        cls,
        tzid: str,
        tzp: TZP = tzp,
        first_date: date = _DEFAULT_FIRST_DATE,
        last_date: date = _DEFAULT_LAST_DATE,
    ) -> Timezone:
        """Create a VTIMEZONE from a tzid like ``"Europe/Berlin"``.

        :param tzid: the id of the timezone
        :param tzp: the timezone provider
        :param first_date: a datetime that is earlier than anything that happens in the calendar
        :param last_date: a datetime that is later than anything that happens in the calendar
        :raises ValueError: If the tzid is unknown.

        >>> from icalendar import Timezone
        >>> tz = Timezone.from_tzid("Europe/Berlin")
        >>> print(tz.to_ical()[:36])
        BEGIN:VTIMEZONE
        TZID:Europe/Berlin

        .. note::
            This can take some time. Please cache the results.
        """
        tz = tzp.timezone(tzid)
        if tz is None:
            raise ValueError(f"Unkown timezone {tzid}.")
        return cls.from_tzinfo(tz, tzid, first_date, last_date)

    @property
    def standard(self) -> list[TimezoneStandard]:
        """The STANDARD subcomponents as a list."""
        return self.walk("STANDARD")

    @property
    def daylight(self) -> list[TimezoneDaylight]:
        """The DAYLIGHT subcomponents as a list.

        These are for the daylight saving time.
        """
        return self.walk("DAYLIGHT")


class TimezoneStandard(Component):
    """
    The "STANDARD" sub-component of "VTIMEZONE" defines the standard
    time offset from UTC for a time zone. It represents a time zone's
    standard time, typically used during winter months in locations
    that observe Daylight Saving Time.
    """

    name = "STANDARD"
    required = ("DTSTART", "TZOFFSETTO", "TZOFFSETFROM")
    singletons = (
        "DTSTART",
        "TZOFFSETTO",
        "TZOFFSETFROM",
    )
    multiple = ("COMMENT", "RDATE", "TZNAME", "RRULE", "EXDATE")

    DTSTART = create_single_property(
        "DTSTART",
        "dt",
        (datetime,),
        datetime,
        """The mandatory "DTSTART" property gives the effective onset date
        and local time for the time zone sub-component definition.
        "DTSTART" in this usage MUST be specified as a date with a local
        time value.""",
    )
    TZOFFSETTO = create_single_property(
        "TZOFFSETTO",
        "td",
        (timedelta,),
        timedelta,
        """The mandatory "TZOFFSETTO" property gives the UTC offset for the
        time zone sub-component (Standard Time or Daylight Saving Time)
        when this observance is in use.
        """,
        vUTCOffset,
    )
    TZOFFSETFROM = create_single_property(
        "TZOFFSETFROM",
        "td",
        (timedelta,),
        timedelta,
        """The mandatory "TZOFFSETFROM" property gives the UTC offset that is
        in use when the onset of this time zone observance begins.
        "TZOFFSETFROM" is combined with "DTSTART" to define the effective
        onset for the time zone sub-component definition.  For example,
        the following represents the time at which the observance of
        Standard Time took effect in Fall 1967 for New York City:

            DTSTART:19671029T020000
            TZOFFSETFROM:-0400
        """,
        vUTCOffset,
    )
    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property


class TimezoneDaylight(Component):
    """
    The "DAYLIGHT" sub-component of "VTIMEZONE" defines the daylight
    saving time offset from UTC for a time zone. It represents a time
    zone's daylight saving time, typically used during summer months
    in locations that observe Daylight Saving Time.
    """

    name = "DAYLIGHT"
    required = TimezoneStandard.required
    singletons = TimezoneStandard.singletons
    multiple = TimezoneStandard.multiple

    DTSTART = TimezoneStandard.DTSTART
    TZOFFSETTO = TimezoneStandard.TZOFFSETTO
    TZOFFSETFROM = TimezoneStandard.TZOFFSETFROM

    rdates = rdates_property
    exdates = exdates_property
    rrules = rrules_property

class Alarm(Component):
    """
    A "VALARM" calendar component is a grouping of component
    properties that defines an alarm or reminder for an event or a
    to-do. For example, it may be used to define a reminder for a
    pending event or an overdue to-do.
    """

    name = "VALARM"
    # some properties MAY/MUST/MUST NOT appear depending on ACTION value
    required = (
        "ACTION",
        "TRIGGER",
    )
    singletons = (
        "ATTACH",
        "ACTION",
        "DESCRIPTION",
        "SUMMARY",
        "TRIGGER",
        "DURATION",
        "REPEAT",
        "UID",
        "PROXIMITY",
        "ACKNOWLEDGED",
    )
    inclusive = (
        (
            "DURATION",
            "REPEAT",
        ),
        (
            "SUMMARY",
            "ATTENDEE",
        ),
    )
    multiple = ("ATTENDEE", "ATTACH", "RELATED-TO")

    REPEAT = single_int_property(
        "REPEAT", 0,
        """The REPEAT property of an alarm component.

        The alarm can be defined such that it triggers repeatedly.  A
        definition of an alarm with a repeating trigger MUST include both
        the "DURATION" and "REPEAT" properties.  The "DURATION" property
        specifies the delay period, after which the alarm will repeat.
        The "REPEAT" property specifies the number of additional
        repetitions that the alarm will be triggered.  This repetition
        count is in addition to the initial triggering of the alarm.
        """
    )

    DURATION = property(
        _get_duration,
        _set_duration,
        _del_duration,
        """The DURATION property of an alarm component.

    The alarm can be defined such that it triggers repeatedly.  A
    definition of an alarm with a repeating trigger MUST include both
    the "DURATION" and "REPEAT" properties.  The "DURATION" property
    specifies the delay period, after which the alarm will repeat.
    """,
    )

    ACKNOWLEDGED = single_utc_property(
        "ACKNOWLEDGED",
        """This is defined in RFC 9074:

    Purpose: This property specifies the UTC date and time at which the
    corresponding alarm was last sent or acknowledged.

    This property is used to specify when an alarm was last sent or acknowledged.
    This allows clients to determine when a pending alarm has been acknowledged
    by a calendar user so that any alerts can be dismissed across multiple devices.
    It also allows clients to track repeating alarms or alarms on recurring events or
    to-dos to ensure that the right number of missed alarms can be tracked.

    Clients SHOULD set this property to the current date-time value in UTC
    when a calendar user acknowledges a pending alarm. Certain kinds of alarms,
    such as email-based alerts, might not provide feedback as to when the calendar user
    sees them. For those kinds of alarms, the client SHOULD set this property
    when the alarm is triggered and the action is successfully carried out.

    When an alarm is triggered on a client, clients can check to see if an "ACKNOWLEDGED"
    property is present. If it is, and the value of that property is greater than or
    equal to the computed trigger time for the alarm, then the client SHOULD NOT trigger
    the alarm. Similarly, if an alarm has been triggered and
    an "alert" has been presented to a calendar user, clients can monitor
    the iCalendar data to determine whether an "ACKNOWLEDGED" property is added or
    changed in the alarm component. If the value of any "ACKNOWLEDGED" property
    in the alarm changes and is greater than or equal to the trigger time of the alarm,
    then clients SHOULD dismiss or cancel any "alert" presented to the calendar user.
    """,
    )

    TRIGGER = create_single_property(
        "TRIGGER",
        "dt",
        (datetime, timedelta),
        Optional[Union[timedelta, datetime]],
        """Purpose:  This property specifies when an alarm will trigger.

    Value Type:  The default value type is DURATION.  The value type can
    be set to a DATE-TIME value type, in which case the value MUST
    specify a UTC-formatted DATE-TIME value.

    Either a positive or negative duration may be specified for the
    "TRIGGER" property.  An alarm with a positive duration is
    triggered after the associated start or end of the event or to-do.
    An alarm with a negative duration is triggered before the
    associated start or end of the event or to-do.""",
    )

    @property
    def TRIGGER_RELATED(self) -> str:
        """The RELATED parameter of the TRIGGER property.

        Values are either "START" (default) or "END".

        A value of START will set the alarm to trigger off the
        start of the associated event or to-do.  A value of END will set
        the alarm to trigger off the end of the associated event or to-do.

        In this example, we create an alarm that triggers two hours after the
        end of its parent component:

        >>> from icalendar import Alarm
        >>> from datetime import timedelta
        >>> alarm = Alarm()
        >>> alarm.TRIGGER = timedelta(hours=2)
        >>> alarm.TRIGGER_RELATED = "END"
        """
        trigger = self.get("TRIGGER")
        if trigger is None:
            return "START"
        return trigger.params.get("RELATED", "START")

    @TRIGGER_RELATED.setter
    def TRIGGER_RELATED(self, value: str):
        """Set "START" or "END"."""
        trigger = self.get("TRIGGER")
        if trigger is None:
            raise ValueError(
                "You must set a TRIGGER before setting the RELATED parameter."
            )
        trigger.params["RELATED"] = value

    class Triggers(NamedTuple):
        """The computed times of alarm triggers.

        start - triggers relative to the start of the Event or Todo (timedelta)

        end - triggers relative to the end of the Event or Todo (timedelta)

        absolute - triggers at a datetime in UTC
        """

        start: tuple[timedelta]
        end: tuple[timedelta]
        absolute: tuple[datetime]

    @property
    def triggers(self):
        """The computed triggers of an Alarm.

        This takes the TRIGGER, DURATION and REPEAT properties into account.

        Here, we create an alarm that triggers 3 times before the start of the
        parent component:

        >>> from icalendar import Alarm
        >>> from datetime import timedelta
        >>> alarm = Alarm()
        >>> alarm.TRIGGER = timedelta(hours=-4)  # trigger 4 hours before START
        >>> alarm.DURATION = timedelta(hours=1)  # after 1 hour trigger again
        >>> alarm.REPEAT = 2  # trigger 2 more times
        >>> alarm.triggers.start == (timedelta(hours=-4),  timedelta(hours=-3),  timedelta(hours=-2))
        True
        >>> alarm.triggers.end
        ()
        >>> alarm.triggers.absolute
        ()
        """
        start = []
        end = []
        absolute = []
        trigger = self.TRIGGER
        if trigger is not None:
            if isinstance(trigger, date):
                absolute.append(trigger)
                add = absolute
            elif self.TRIGGER_RELATED == "START":
                start.append(trigger)
                add = start
            else:
                end.append(trigger)
                add = end
            duration = self.DURATION
            if duration is not None:
                for _ in range(self.REPEAT):
                    add.append(add[-1] + duration)
        return self.Triggers(
            start=tuple(start), end=tuple(end), absolute=tuple(absolute)
        )


class Calendar(Component):
    """
    The "VCALENDAR" object is a collection of calendar information.
    This information can include a variety of components, such as
    "VEVENT", "VTODO", "VJOURNAL", "VFREEBUSY", "VTIMEZONE", or any
    other type of calendar component.
    """

    name = "VCALENDAR"
    canonical_order = (
        "VERSION",
        "PRODID",
        "CALSCALE",
        "METHOD",
        "DESCRIPTION",
        "X-WR-CALDESC",
        "NAME",
        "X-WR-CALNAME",
    )
    required = (
        "PRODID",
        "VERSION",
    )
    singletons = (
        "PRODID",
        "VERSION",
        "CALSCALE",
        "METHOD",
        "COLOR",  # RFC 7986
    )
    multiple = (
        "CATEGORIES",  # RFC 7986
        "DESCRIPTION",  # RFC 7986
        "NAME",  # RFC 7986
    )

    @classmethod
    def example(cls, name: str = "example") -> Calendar:
        """Return the calendar example with the given name."""
        return cls.from_ical(get_example("calendars", name))

    @classmethod
    def from_ical(cls, st, multiple=False):
        comps = Component.from_ical(st, multiple=True)
        all_timezones_so_far = True
        for comp in comps:
            for component in comp.subcomponents:
                if component.name == 'VTIMEZONE':
                    if all_timezones_so_far:
                        pass
                    else:
                        # If a preceding component refers to a VTIMEZONE defined later in the source st
                        # (forward references are allowed by RFC 5545), then the earlier component may have
                        # the wrong timezone attached.
                        # However, during computation of comps, all VTIMEZONEs observed do end up in
                        # the timezone cache. So simply re-running from_ical will rely on the cache
                        # for those forward references to produce the correct result.
                        # See test_create_america_new_york_forward_reference.
                        return Component.from_ical(st, multiple)
                else:
                    all_timezones_so_far = False

        # No potentially forward VTIMEZONEs to worry about
        if multiple:
            return comps
        if len(comps) > 1:
            raise ValueError(cls._format_error(
                'Found multiple components where only one is allowed', st))
        if len(comps) < 1:
            raise ValueError(cls._format_error(
                'Found no components where exactly one is required', st))
        return comps[0]

    @property
    def events(self) -> list[Event]:
        """All event components in the calendar.

        This is a shortcut to get all events.
        Modifications do not change the calendar.
        Use :py:meth:`Component.add_component`.

        >>> from icalendar import Calendar
        >>> calendar = Calendar.example()
        >>> event = calendar.events[0]
        >>> event.start
        datetime.date(2022, 1, 1)
        >>> print(event["SUMMARY"])
        New Year's Day
        """
        return self.walk("VEVENT")

    @property
    def todos(self) -> list[Todo]:
        """All todo components in the calendar.

        This is a shortcut to get all todos.
        Modifications do not change the calendar.
        Use :py:meth:`Component.add_component`.
        """
        return self.walk("VTODO")

    @property
    def freebusy(self) -> list[FreeBusy]:
        """All FreeBusy components in the calendar.

        This is a shortcut to get all FreeBusy.
        Modifications do not change the calendar.
        Use :py:meth:`Component.add_component`.
        """
        return self.walk("VFREEBUSY")

    def get_used_tzids(self) -> set[str]:
        """The set of TZIDs in use.

        This goes through the whole calendar to find all occurrences of
        timezone information like the TZID parameter in all attributes.

        >>> from icalendar import Calendar
        >>> calendar = Calendar.example("timezone_rdate")
        >>> calendar.get_used_tzids()
        {'posix/Europe/Vaduz'}

        Even if you use UTC, this will not show up.
        """
        result = set()
        for name, value in self.property_items(sorted=False):
            if hasattr(value, "params"):
                result.add(value.params.get("TZID"))
        return result - {None}

    def get_missing_tzids(self) -> set[str]:
        """The set of missing timezone component tzids.

        To create a :rfc:`5545` compatible calendar,
        all of these timezones should be added.
        """
        tzids = self.get_used_tzids()
        for timezone in self.timezones:
            tzids.remove(timezone.tz_name)
        return tzids

    @property
    def timezones(self) -> list[Timezone]:
        """Return the timezones components in this calendar.

        >>> from icalendar import Calendar
        >>> calendar = Calendar.example("pacific_fiji")
        >>> [timezone.tz_name for timezone in calendar.timezones]
        ['custom_Pacific/Fiji']

        .. note::

            This is a read-only property.
        """
        return self.walk("VTIMEZONE")

    def add_missing_timezones(
        self,
        first_date: date = Timezone._DEFAULT_FIRST_DATE,
        last_date: date = Timezone._DEFAULT_LAST_DATE,
    ):
        """Add all missing VTIMEZONE components.

        This adds all the timezone components that are required.

        .. note::

            Timezones that are not known will not be added.

        :param first_date: earlier than anything that happens in the calendar
        :param last_date: later than anything happening in the calendar

        >>> from icalendar import Calendar, Event
        >>> from datetime import datetime
        >>> from zoneinfo import ZoneInfo
        >>> calendar = Calendar()
        >>> event = Event()
        >>> calendar.add_component(event)
        >>> event.start = datetime(1990, 10, 11, 12, tzinfo=ZoneInfo("Europe/Berlin"))
        >>> calendar.timezones
        []
        >>> calendar.add_missing_timezones()
        >>> calendar.timezones[0].tz_name
        'Europe/Berlin'
        >>> calendar.get_missing_tzids()  # check that all are added
        set()
        """
        for tzid in self.get_missing_tzids():
            try:
                timezone = Timezone.from_tzid(
                    tzid, first_date=first_date, last_date=last_date
                )
            except ValueError:
                continue
            self.add_component(timezone)

    calendar_name = multi_language_text_property(
        "NAME", "X-WR-CALNAME",
        """This property specifies the name of the calendar.

    This implements :rfc:`7986` ``NAME`` and ``X-WR-CALNAME``.

    Property Parameters:
        IANA, non-standard, alternate text
        representation, and language property parameters can be specified
        on this property.

    Conformance:
        This property can be specified multiple times in an
        iCalendar object.  However, each property MUST represent the name
        of the calendar in a different language.

    Description:
        This property is used to specify a name of the
        iCalendar object that can be used by calendar user agents when
        presenting the calendar data to a user.  Whilst a calendar only
        has a single name, multiple language variants can be specified by
        including this property multiple times with different "LANGUAGE"
        parameter values on each.

    Example:
        Below, we set the name of the calendar.

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.calendar_name = "My Calendar"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            NAME:My Calendar
            END:VCALENDAR
    """)

    description = multi_language_text_property(
        "DESCRIPTION", "X-WR-CALDESC",
        """This property specifies the description of the calendar.

    This implements :rfc:`7986` ``DESCRIPTION`` and ``X-WR-CALDESC``.

    Conformance:
        This property can be specified multiple times in an
        iCalendar object.  However, each property MUST represent the
        description of the calendar in a different language.

    Description:
        This property is used to specify a lengthy textual
        description of the iCalendar object that can be used by calendar
        user agents when describing the nature of the calendar data to a
        user.  Whilst a calendar only has a single description, multiple
        language variants can be specified by including this property
        multiple times with different "LANGUAGE" parameter values on each.

    Example:
        Below, we add a description to a calendar.

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.description = "This is a calendar"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            DESCRIPTION:This is a calendar
            END:VCALENDAR
    """)

    color = single_string_property(
        "COLOR",
        """This property specifies a color used for displaying the calendar.

    This implements :rfc:`7986` ``COLOR`` and ``X-APPLE-CALENDAR-COLOR``.
    Please note that since :rfc:`7986`, subcomponents can have their own color.

    Property Parameters:
        IANA and non-standard property parameters can
        be specified on this property.

    Conformance:
        This property can be specified once in an iCalendar
        object or in ``VEVENT``, ``VTODO``, or ``VJOURNAL`` calendar components.

    Description:
        This property specifies a color that clients MAY use
        when presenting the relevant data to a user.  Typically, this
        would appear as the "background" color of events or tasks.  The
        value is a case-insensitive color name taken from the CSS3 set of
        names, defined in Section 4.3 of `W3C.REC-css3-color-20110607 <https://www.w3.org/TR/css-color-3/>`_.

    Example:
        ``"turquoise"``, ``"#ffffff"``

        .. code-block:: pycon

            >>> from icalendar import Calendar
            >>> calendar = Calendar()
            >>> calendar.color = "black"
            >>> print(calendar.to_ical())
            BEGIN:VCALENDAR
            COLOR:black
            END:VCALENDAR

    """,
    "X-APPLE-CALENDAR-COLOR",
    )
    categories = categories_property

# These are read only singleton, so one instance is enough for the module
types_factory = TypesFactory()
component_factory = ComponentFactory()

__all__ = [
    "Alarm",
    "Calendar",
    "Component",
    "ComponentFactory",
    "Event",
    "FreeBusy",
    "INLINE",
    "Journal",
    "Timezone",
    "TimezoneDaylight",
    "TimezoneStandard",
    "Todo",
    "component_factory",
    "get_example",
    "IncompleteComponent",
]
