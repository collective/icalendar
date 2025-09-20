"""The base for :rfc:`5545` components."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, ClassVar, Optional

from icalendar.attr import comments_property, single_utc_property, uid_property
from icalendar.cal.component_factory import ComponentFactory
from icalendar.caselessdict import CaselessDict
from icalendar.error import InvalidCalendar
from icalendar.parser import Contentline, Contentlines, Parameters, q_join, q_split
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.prop import TypesFactory, vDDDLists, vText
from icalendar.timezone import tzp

if TYPE_CHECKING:
    from icalendar.compatibility import Self

_marker = []


class Component(CaselessDict):
    """Base class for calendar components.

    Component is the base object for calendar, Event and the other
    components defined in :rfc:`5545`. Normally you will not use this class
    directly, but rather one of the subclasses.

    Attributes:
        name: The name of the component. Example: ``VCALENDAR``.
        required: These properties are required.
        singletons: These properties must only appear once.
        multiple: These properties may occur more than once.
        exclusive: These properties are mutually exclusive.
        inclusive: If the first in a tuple occurs, the second one must also occur.
        ignore_exceptions: If True, and we cannot parse this
            component, we will silently ignore it, rather than let the
            exception propagate upwards.
        types_factory: Factory for property types
    """

    name = None  # should be defined in each component
    required = ()  # These properties are required
    singletons = ()  # These properties must only appear once
    multiple = ()  # may occur more than once
    exclusive = ()  # These properties are mutually exclusive
    inclusive: (
        tuple[str] | tuple[tuple[str, str]]
    ) = ()  # if any occurs the other(s) MUST occur
    # ('duration', 'repeat')
    ignore_exceptions = False  # if True, and we cannot parse this
    # component, we will silently ignore
    # it, rather than let the exception
    # propagate upwards
    # not_compliant = ['']  # List of non-compliant properties.

    types_factory = TypesFactory()
    _components_factory: ClassVar[Optional[ComponentFactory]] = None

    @classmethod
    def get_component_class(cls, name: str) -> type[Component]:
        """Return a component with this name.

        Arguments:
            name: Name of the component, i.e. ``VCALENDAR``
        """
        if cls._components_factory is None:
            cls._components_factory = ComponentFactory()
        return cls._components_factory.get(name, Component)

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict."""
        super().__init__(*args, **kwargs)
        # set parameters here for properties that use non-default values
        self.subcomponents: list[Component] = []  # Components can be nested.
        self.errors = []  # If we ignored exception(s) while
        # parsing a property, contains error strings

    def __bool__(self):
        """Returns True, CaselessDict would return False if it had no items."""
        return True

    def is_empty(self):
        """Returns True if Component has no items or subcomponents, else False."""
        return bool(not list(self.values()) + self.subcomponents)

    #############################
    # handling of property values

    @classmethod
    def _encode(cls, name, value, parameters=None, encode=1):
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
        if isinstance(value, cls.types_factory.all_types):
            # Don't encode already encoded values.
            obj = value
        else:
            klass = cls.types_factory.for_property(name)
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

    def add(
        self,
        name: str,
        value,
        parameters: dict[str, str] | Parameters = None,
        encode: bool = True,  # noqa: FBT001
    ):
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
        decoded = self.types_factory.from_ical(name, value)
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
        if default is _marker:
            raise KeyError(name)
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
        self[name] = self.types_factory["inline"](q_join(values))

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
            result += subcomponent._walk(name, select)  # noqa: SLF001
        return result

    def walk(self, name=None, select=lambda _: True) -> list[Component]:
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

    def property_items(
        self,
        recursive=True,
        sorted: bool = True,  # noqa: A002, FBT001
    ) -> list[tuple[str, object]]:
        """Returns properties in this component and subcomponents as:
        [(name, value), ...]
        """
        v_text = self.types_factory["text"]
        properties = [("BEGIN", v_text(self.name).to_ical())]
        property_names = self.sorted_keys() if sorted else self.keys()

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
        properties.append(("END", v_text(self.name).to_ical()))
        return properties

    @classmethod
    def from_ical(cls, st, multiple: bool = False) -> Self | list[Self]:  # noqa: FBT001
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
                c_class = cls.get_component_class(c_name)
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
                factory = cls.types_factory.for_property(name)
                component = stack[-1] if stack else None
                if not component:
                    # only accept X-COMMENT at the end of the .ics file
                    # ignore these components in parsing
                    if uname == "X-COMMENT":
                        break
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
                    # Workaround broken ICS files with empty RDATE
                    elif name == "RDATE" and vals == "":
                        parsed_components = []
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
        return f"{error_description}: {bad_input}"

    def content_line(self, name, value, sorted: bool = True):  # noqa: A002, FBT001
        """Returns property as content line."""
        params = getattr(value, "params", Parameters())
        return Contentline.from_parts(name, params, value, sorted=sorted)

    def content_lines(self, sorted: bool = True):  # noqa: A002, FBT001
        """Converts the Component and subcomponents into content lines."""
        contentlines = Contentlines()
        for name, value in self.property_items(sorted=sorted):
            cl = self.content_line(name, value, sorted=sorted)
            contentlines.append(cl)
        contentlines.append("")  # remember the empty string in the end
        return contentlines

    def to_ical(self, sorted: bool = True):  # noqa: A002, FBT001
        """
        :param sorted: Whether parameters and properties should be
                       lexicographically sorted.
        """

        content_lines = self.content_lines(sorted=sorted)
        return content_lines.to_ical()

    def __repr__(self):
        """String representation of class with all of it's subcomponents."""
        subs = ", ".join(str(it) for it in self.subcomponents)
        return (
            f"{self.name or type(self).__name__}"
            f"({dict(self)}{', ' + subs if subs else ''})"
        )

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

    DTSTAMP = stamp = single_utc_property(
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

    @property
    def last_modified(self) -> datetime:
        """Datetime when the information associated with the component was last revised.

        Since :attr:`LAST_MODIFIED` is an optional property,
        this returns :attr:`DTSTAMP` if :attr:`LAST_MODIFIED` is not set.
        """
        return self.LAST_MODIFIED or self.DTSTAMP

    @last_modified.setter
    def last_modified(self, value):
        self.LAST_MODIFIED = value

    @last_modified.deleter
    def last_modified(self):
        del self.LAST_MODIFIED

    @property
    def created(self) -> datetime:
        """Datetime when the information associated with the component was created.

        Since :attr:`CREATED` is an optional property,
        this returns :attr:`DTSTAMP` if :attr:`CREATED` is not set.
        """
        return self.CREATED or self.DTSTAMP

    @created.setter
    def created(self, value):
        self.CREATED = value

    @created.deleter
    def created(self):
        del self.CREATED

    def is_thunderbird(self) -> bool:
        """Whether this component has attributes that indicate that Mozilla Thunderbird created it."""  # noqa: E501
        return any(attr.startswith("X-MOZ-") for attr in self.keys())

    @staticmethod
    def _utc_now():
        """Return now as UTC value."""
        return datetime.now(timezone.utc)

    uid = uid_property
    comments = comments_property

    CREATED = single_utc_property(
        "CREATED",
        """
        CREATED specifies the date and time that the calendar
        information was created by the calendar user agent in the calendar
        store.

        Conformance:
            The property can be specified once in "VEVENT",
            "VTODO", or "VJOURNAL" calendar components.  The value MUST be
            specified as a date with UTC time.

        """,
    )

    _validate_new = True

    @staticmethod
    def _validate_start_and_end(start, end):
        """This validates start and end.

        Raises:
            InvalidCalendar: If the information is not valid
        """
        if start is None or end is None:
            return
        if start > end:
            raise InvalidCalendar("end must be after start")

    @classmethod
    def new(
        cls,
        created: Optional[date] = None,
        comments: list[str] | str | None = None,
        last_modified: Optional[date] = None,
        stamp: Optional[date] = None,
    ) -> Component:
        """Create a new component.

        Arguments:
            comments: The :attr:`comments` of the component.
            created: The :attr:`created` of the component.
            last_modified: The :attr:`last_modified` of the component.
            stamp: The :attr:`DTSTAMP` of the component.

        Raises:
            InvalidCalendar: If the content is not valid according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the validation.
        """
        component = cls()
        component.DTSTAMP = stamp
        component.created = created
        component.last_modified = last_modified
        component.comments = comments
        return component


__all__ = ["Component"]
