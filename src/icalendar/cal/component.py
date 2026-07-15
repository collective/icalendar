"""The base for :rfc:`5545` components."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal, overload

from icalendar.attr import (
    CONCEPTS_TYPE_SETTER,
    LINKS_TYPE_SETTER,
    RELATED_TO_TYPE_SETTER,
    comments_property,
    concepts_property,
    links_property,
    refids_property,
    related_to_property,
    single_utc_property,
    uid_property,
)
from icalendar.cal.component_factory import ComponentFactory
from icalendar.caselessdict import CaselessDict
from icalendar.error import InvalidCalendar, JCalParsingError
from icalendar.parser import (
    Contentline,
    Contentlines,
    Parameters,
    q_join,
    q_split,
)
from icalendar.parser.ical.component import ComponentIcalParser
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.prop import VPROPERTY, TypesFactory, vDDDLists, vText
from icalendar.timezone import tzp
from icalendar.tools import is_date

if TYPE_CHECKING:
    from collections.abc import Iterable

    from icalendar.compatibility import Self

_marker = []


@dataclass
class _ComponentEqFrame:
    """A pending component-equality comparison on the iterative stack.

    See ``Component.__eq__`` for how the fields are used.
    """

    #: the two components being compared
    a: Component
    b: Component
    #: ``b``'s subcomponents not yet matched against one of ``a``'s. ``None``
    #: until ``a`` and ``b``'s own properties have been compared and found equal.
    unmatched: list | None = None
    #: index of the ``a`` subcomponent we are currently trying to match
    a_index: int = 0
    #: index of the unmatched ``b`` subcomponent we are currently testing
    candidate_index: int = 0


class Component(CaselessDict):
    """Base class for calendar components.

    Component is the base object for calendar, Event and the other
    components defined in :rfc:`5545`. Normally you will not use this class
    directly, but rather one of the subclasses.
    """

    name: ClassVar[str | None] = None
    """The name of the component.

    This is defined in each component class.

    Example:

        ..  code-block:: pycon

            >>> from icalendar import Calendar
            >>> cal = Calendar.new()
            >>> cal.name
            'VCALENDAR'

    """

    required: ClassVar[tuple[()]] = ()
    """These properties are required."""

    singletons: ClassVar[tuple[()]] = ()
    """These properties must appear only once."""

    multiple: ClassVar[tuple[()]] = ()
    """These properties may occur more than once."""

    exclusive: ClassVar[tuple[()]] = ()
    """These properties are mutually exclusive."""

    inclusive: ClassVar[(tuple[str] | tuple[tuple[str, str]])] = ()
    """These properties are inclusive.

    In other words, if the first property in the tuple occurs, then the
    second one must also occur.

    Example:

        .. code-block:: python

            ('duration', 'repeat')
    """

    ignore_exceptions: ClassVar[bool] = False
    """Whether or not to ignore exceptions when parsing.

    If ``True``, and this component can't be parsed, then it will silently
    ignore it, rather than let the exception propagate upwards.
    """

    types_factory: ClassVar[TypesFactory] = TypesFactory.instance()
    _components_factory: ClassVar[ComponentFactory | None] = None

    subcomponents: list[Component]
    """All subcomponents of this component."""

    @classmethod
    def _get_component_factory(cls) -> ComponentFactory:
        """Get the component factory."""
        if cls._components_factory is None:
            cls._components_factory = ComponentFactory()
        return cls._components_factory

    @classmethod
    def get_component_class(cls, name: str) -> type[Component]:
        """Return a component with this name.

        Parameters:
            name: Name of the component, i.e. ``VCALENDAR``
        """
        return cls._get_component_factory().get_component_class(name)

    @classmethod
    def register(cls, component_class: type[Component]) -> None:
        """Register a custom component class.

        Parameters:
            component_class: Component subclass to register.
                Must have a ``name`` attribute.

        Raises:
            ValueError: If ``component_class`` has no ``name`` attribute.
            ValueError: If a component with this name is already registered.

        Examples:
            Create a custom icalendar component with the name ``X-EXAMPLE``:

            .. code-block:: pycon

                >>> from icalendar import Component
                >>> class XExample(Component):
                ...     name = "X-EXAMPLE"
                ...     def custom_method(self):
                ...         return "custom"
                >>> Component.register(XExample)
        """
        if not hasattr(component_class, "name") or component_class.name is None:
            raise ValueError(f"{component_class} must have a 'name' attribute")

        # Check if already registered
        component_factory = cls._get_component_factory()
        existing = component_factory.get(component_class.name)
        if existing is not None and existing is not component_class:
            raise ValueError(
                f"Component '{component_class.name}' is already registered"
                f" as {existing}"
            )

        component_factory.add_component_class(component_class)

    @staticmethod
    def _infer_value_type(
        value: date | datetime | timedelta | time | tuple | list,
    ) -> str | None:
        """Infer the ``VALUE`` parameter from a Python type.

        Parameters:
            value: Python native type, one of :class:`datetime.date`, :class:`datetime.datetime`,
                :class:`datetime.timedelta`, :class:`datetime.time`, :class:`tuple`,
                or :class:`list`.

        Returns:
            str or None: The ``VALUE`` parameter string, for example, "DATE",
                "TIME", or other string, or ``None``
                if no specific ``VALUE`` is needed.
        """
        if isinstance(value, list):
            if not value:
                return None
            # Check if ALL items are date (but not datetime)
            if all(is_date(item) for item in value):
                return "DATE"
            # Check if ALL items are time
            if all(isinstance(item, time) for item in value):
                return "TIME"
            # Mixed types or other types - don't infer
            return None
        if is_date(value):
            return "DATE"
        if isinstance(value, time):
            return "TIME"
        # Don't infer PERIOD - it's too risky and vPeriod already handles it
        return None

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict."""
        super().__init__(*args, **kwargs)
        # set parameters here for properties that use non-default values
        self.subcomponents: list[Component] = []  # Components can be nested.
        self.errors = []  # If we ignored exception(s) while
        # parsing a property, contains error strings

    def __bool__(self) -> bool:
        """Returns True, CaselessDict would return False if it had no items."""
        return True

    def __getitem__(self, key) -> VPROPERTY:
        """Get property value from the component dictionary."""
        return super().__getitem__(key)

    def get(self, key, default=None) -> Any:
        """Get property value with default."""
        try:
            return self[key]
        except KeyError:
            return default

    def is_empty(self) -> bool:
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
            # Extract VALUE parameter if present, or infer it from the Python type
            value_param = None
            if parameters and "VALUE" in parameters:
                value_param = parameters["VALUE"]
            elif not isinstance(value, cls.types_factory.all_types):
                inferred = cls._infer_value_type(value)
                if inferred:
                    value_param = inferred
                    # Auto-set the VALUE parameter
                    if parameters is None:
                        parameters = {}
                    if "VALUE" not in parameters:
                        parameters["VALUE"] = inferred

            klass = cls.types_factory.for_property(name, value_param)
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
        encode: bool = True,
    ) -> None:
        """Add a property to this component.

        If the property already exists, the new value is appended so the
        property carries a list of values rather than replacing the previous
        one. When ``name`` is ``DTSTAMP``, ``CREATED``, or ``LAST-MODIFIED``
        and ``value`` is a ``datetime``, the value is converted to UTC as the
        RFC requires.

        Parameters:
            name: Name of the property.
            value:
                Value of the property. Either a basic Python type or any of
                icalendar's own property types.
            parameters:
                Property parameter dictionary for the value. Only consulted
                when ``encode`` is ``True``.
            encode:
                ``True`` if the value should be encoded to one of icalendar's
                own property types (fallback is ``vText``); ``False`` to
                store the value as-is.

        Returns:
            ``None``

        Example:

            >>> from icalendar import Event
            >>> event = Event()
            >>> event.add("summary", "Team sync")
            >>> event["summary"]
            vText(b'Team sync')

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

    def _decode(self, name: str, value: VPROPERTY):
        """Internal for decoding property values."""

        # TODO: Currently the decoded method calls the icalendar.prop instances
        # from_ical. We probably want to decode properties into Python native
        # types here. But when parsing from an ical string with from_ical, we
        # want to encode the string into a real icalendar.prop property.
        if hasattr(value, "ical_value"):
            return value.ical_value
        if isinstance(value, vDDDLists):
            # TODO: Workaround unfinished decoding
            return value
        decoded = self.types_factory.from_ical(name, value)
        # TODO: remove when proper decoded is implemented in every prop.* class
        # Workaround to decode vText properly
        if isinstance(decoded, vText):
            decoded = decoded.encode(DEFAULT_ENCODING)
        return decoded

    def decoded(self, name: str, default: Any = _marker) -> Any:
        """Returns decoded value of property.

        A component maps keys to icalendar property value types.
        This function returns values compatible to native Python types.
        """
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

    def add_component(self, component: Component) -> None:
        """Add a subcomponent to this component."""
        self.subcomponents.append(component)

    def _walk(
        self, name: str | None, select: callable[[Component], bool]
    ) -> list[Component]:
        """Walk to given component."""
        result = []
        stack = [self]
        while stack:
            component = stack.pop()
            if (name is None or component.name == name) and select(component):
                result.append(component)
            stack.extend(reversed(component.subcomponents))
        return result

    def walk(
        self,
        name: str | None = None,
        select: callable[[Component], bool] = lambda _: True,
    ) -> list[Component]:
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

    def with_uid(self, uid: str) -> list[Component]:
        """Return a list of components with the given UID.

        Parameters:
            uid: The UID of the component.

        Returns:
            list[Component]: List of components with the given UID.
        """
        return self.walk(select=lambda c: c.uid == uid)

    #####################
    # Generation

    def property_items(
        self,
        recursive: bool = True,
        sorted: bool = True,
    ) -> list[tuple[str, object]]:
        """Returns properties in this component and subcomponents as:
        [(name, value), ...]
        """
        # Iterative implementation to avoid RecursionError
        result = []
        v_text = self.types_factory["text"]
        # Stack stores (component, state)
        # state: True means we are processing the END of the component
        # state: False means we are processing the BEGIN and properties of the component
        stack = [(self, False)]
        while stack:
            comp, is_end = stack.pop()
            if is_end:
                result.append(("END", v_text(comp.name).to_ical()))
            else:
                result.append(("BEGIN", v_text(comp.name).to_ical()))
                property_names = comp.sorted_keys() if sorted else comp.keys()

                for name in property_names:
                    values = comp[name]
                    if isinstance(values, list):
                        # normally one property is one line
                        for value in values:
                            result.append((name, value))
                    else:
                        result.append((name, values))

                # Push the END marker for this component
                stack.append((comp, True))
                # Push subcomponents if recursion is enabled
                if recursive:
                    # Push in reverse order to maintain original order in result
                    for subcomponent in reversed(comp.subcomponents):
                        stack.append((subcomponent, False))

        return result

    @overload
    @classmethod
    def from_ical(
        cls, st: str | bytes, multiple: Literal[False] = False
    ) -> Component: ...

    @overload
    @classmethod
    def from_ical(cls, st: str | bytes, multiple: Literal[True]) -> list[Component]: ...

    @classmethod
    def _get_ical_parser(cls, st: str | bytes) -> ComponentIcalParser:
        """Get the iCal parser for the given input string."""
        return ComponentIcalParser(st, cls._get_component_factory(), cls.types_factory)

    @classmethod
    def from_ical(
        cls, st: str | bytes | Path, multiple: bool = False
    ) -> Component | list[Component]:
        """Parse iCalendar data into component instances.

        Handles standard and custom components (``X-*``, IANA-registered).

        Parameters:
            st: iCalendar data as bytes or string, or a path to an iCalendar file as
                :class:`pathlib.Path` or string.
            multiple: If ``True``, returns list. If ``False``, returns single component.

        Returns:
            Component or list of components

        See Also:
            :doc:`/how-to/custom-components` for examples of parsing custom components
        """
        if isinstance(st, Path):
            st = st.read_bytes()
        elif isinstance(st, str) and "\n" not in st and "\r" not in st:
            # A string is only probed as a file path when it contains no line
            # breaks. Valid iCalendar data is always folded with CRLF line
            # endings (RFC 5545), so real calendar content never reaches this
            # branch and is never read from disk. File paths, conversely, do
            # not contain line breaks on the platforms we support.
            try:
                is_file = Path(st).is_file()
            except (OSError, ValueError):
                # The string is not usable as a path on this platform (e.g. it
                # is too long, or contains characters the OS rejects such as an
                # embedded null byte). Treat it as calendar data, not a file, so
                # the parser raises a consistent ValueError across platforms.
                is_file = False
            if is_file:
                st = Path(st).read_bytes()
        parser = cls._get_ical_parser(st)
        components = parser.parse()
        if multiple:
            return components
        if len(components) > 1:
            raise ValueError(
                cls._format_error(
                    "Found multiple components where only one is allowed", st
                )
            )
        if len(components) < 1:
            raise ValueError(
                cls._format_error(
                    "Found no components where exactly one is required", st
                )
            )
        return components[0]

    @staticmethod
    def _format_error(error_description, bad_input, elipsis="[...]"):
        # there's three character more in the error, ie. ' ' x2 and a ':'
        max_error_length = 100 - 3
        if len(error_description) + len(bad_input) + len(elipsis) > max_error_length:
            truncate_to = max_error_length - len(error_description) - len(elipsis)
            return f"{error_description}: {bad_input[:truncate_to]} {elipsis}"
        return f"{error_description}: {bad_input}"

    def content_line(self, name, value, sorted: bool = True):
        """Returns property as content line."""
        params = getattr(value, "params", Parameters())
        return Contentline.from_parts(name, params, value, sorted=sorted)

    def content_lines(self, sorted: bool = True):
        """Converts the Component and subcomponents into content lines."""
        contentlines = Contentlines()
        for name, value in self.property_items(sorted=sorted):
            cl = self.content_line(name, value, sorted=sorted)
            contentlines.append(cl)
        contentlines.append("")  # remember the empty string in the end
        return contentlines

    def to_ical(self, sorted: bool = True):
        """
        :param sorted: Whether parameters and properties should be
                       lexicographically sorted.
        """

        content_lines = self.content_lines(sorted=sorted)
        return content_lines.to_ical()

    def __repr__(self) -> str:
        """String representation of class with all of its subcomponents.

        Implemented iteratively rather than recursively so that calendars
        with deeply nested subcomponents do not raise ``RecursionError``.
        A pathological ``.ics`` payload of only ~13 KB can otherwise nest
        ``BEGIN:VEVENT`` ~500 levels and crash any caller that performs
        ``repr()``/``str()``/``f"{cal}"`` on the parsed calendar
        (e.g. logging, error reporting, debug pages).
        """
        # Stack-based traversal. Each frame is one of:
        #   ("open", component)   -> emit "Name({props}" and schedule children
        #   ("close",)            -> emit ")"
        #   ("comma",)            -> emit ", "
        out: list[str] = []
        stack: list[tuple] = [("open", self)]
        while stack:
            frame = stack.pop()
            kind = frame[0]
            if kind == "comma":
                out.append(", ")
            elif kind == "close":
                out.append(")")
            else:  # "open"
                node = frame[1]
                if isinstance(node, Component):
                    out.append(f"{node.name or type(node).__name__}({dict(node)}")
                    subs = node.subcomponents
                    if subs:
                        # Defer ")" then push children in reverse so that
                        # popping yields original order, with ", " separators
                        # (the first popped comma serves as the separator
                        # between the component's dict and its first child).
                        stack.append(("close",))
                        for sub in reversed(subs):
                            stack.append(("open", sub))
                            stack.append(("comma",))
                    else:
                        out.append(")")
                else:
                    # Should not normally occur (subcomponents are Components),
                    # but be safe and fall back to non-recursive str().
                    out.append(str(node))
        return "".join(out)

    def __eq__(self, other: Component) -> bool:
        if not isinstance(other, Component):
            return NotImplemented

        # Two components are equal when their own properties are equal and their
        # subcomponents are equal as a multiset: order does not matter, and each
        # nested pair is compared the same way recursively. Subcomponents are
        # neither sortable nor hashable, so we can't use a set; we have to match
        # each one by searching. Done recursively that search is exponential for
        # deeply nested components (GHSA-cv84-9p8j-fj68), so we walk an explicit
        # stack instead of recursing.
        #
        # Each frame holds the pair being compared plus b's subcomponents
        # still unmatched. child_result carries the outcome of the comparison
        # that just finished back up to its parent frame: a successful child
        # match removes that subcomponent from unmatched and advances to the
        # next a subcomponent, while a failure tries the next candidate.
        # Exhausting a's subcomponents means every one found a partner ->
        # equal; running out of candidates for some subcomponent -> not equal.
        # (Greedy matching is sufficient because equality is transitive, so equal
        # candidates are interchangeable.)
        stack = [_ComponentEqFrame(self, other)]
        child_result = None
        while stack:
            frame = stack[-1]
            if frame.unmatched is None:
                if len(frame.a.subcomponents) != len(frame.b.subcomponents) or not (
                    CaselessDict.__eq__(frame.a, frame.b)
                ):
                    stack.pop()
                    child_result = False
                    continue
                frame.unmatched = list(frame.b.subcomponents)
            elif child_result is not None:
                if child_result:
                    del frame.unmatched[frame.candidate_index]
                    frame.a_index += 1
                    frame.candidate_index = 0
                else:
                    frame.candidate_index += 1
                child_result = None
            if frame.a_index >= len(frame.a.subcomponents):
                stack.pop()
                child_result = True
            elif frame.candidate_index >= len(frame.unmatched):
                stack.pop()
                child_result = False
            else:
                stack.append(
                    _ComponentEqFrame(
                        frame.a.subcomponents[frame.a_index],
                        frame.unmatched[frame.candidate_index],
                    )
                )
        return child_result

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
        """The date and time when a calendar component was last modified.

        This property is commonly used to track revisions to calendar
        components such as VEVENT, VTODO, VJOURNAL, and VTIMEZONE.

        Example:
            Set the LAST-MODIFIED property of an event to a UTC time.

            .. code-block:: pycon

                >>> from datetime import datetime, timezone
                >>> from icalendar import Event
                >>> event = Event()
                >>> event.last_modified = datetime(2026, 5, 31, 23, 52, 45, tzinfo=timezone.utc)
                >>> event.last_modified
                datetime.datetime(2026, 5, 31, 23, 52, 45, tzinfo=ZoneInfo(key='UTC'))
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
        """Whether this component has attributes that indicate that Mozilla Thunderbird created it."""
        return any(attr.startswith("X-MOZ-") for attr in self.keys())

    @staticmethod
    def _utc_now() -> datetime:
        """Return now as UTC value."""
        return datetime.now(timezone.utc)

    uid = uid_property
    comments = comments_property
    links = links_property
    related_to = related_to_property
    concepts = concepts_property
    refids = refids_property

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
            ~error.InvalidCalendar: If the information is not valid
        """
        if start is None or end is None:
            return
        if start > end:
            raise InvalidCalendar("end must be after start")

    @classmethod
    def new(
        cls,
        created: date | None = None,
        comments: list[str] | str | None = None,
        concepts: CONCEPTS_TYPE_SETTER = None,
        last_modified: date | None = None,
        links: LINKS_TYPE_SETTER = None,
        refids: list[str] | str | None = None,
        related_to: RELATED_TO_TYPE_SETTER = None,
        stamp: date | None = None,
        subcomponents: Iterable[Component] | None = None,
    ) -> Component:
        """Create a new component.

        Parameters:
            comments: The :attr:`comments` of the component.
            concepts: The :attr:`concepts` of the component.
            created: The :attr:`created` of the component.
            last_modified: The :attr:`last_modified` of the component.
            links: The :attr:`links` of the component.
            related_to: The :attr:`related_to` of the component.
            stamp: The :attr:`DTSTAMP` of the component.
            subcomponents: The subcomponents of the component.

        Raises:
            ~error.InvalidCalendar: If the content is not valid
                according to :rfc:`5545`.

        .. warning:: As time progresses, we will be stricter with the
            validation.
        """
        component = cls()
        component.DTSTAMP = stamp
        component.created = created
        component.last_modified = last_modified
        component.comments = comments
        component.links = links
        component.related_to = related_to
        component.concepts = concepts
        component.refids = refids
        if subcomponents is not None:
            component.subcomponents = (
                subcomponents
                if isinstance(subcomponents, list)
                else list(subcomponents)
            )
        return component

    def to_jcal(self) -> list:
        """Convert this component to a jCal object.

        Returns:
            jCal object

        See also :attr:`to_json`.

        In this example, we create a simple VEVENT component and convert it to jCal:

        .. code-block:: pycon

            >>> from icalendar import Event
            >>> from datetime import date
            >>> from pprint import pprint
            >>> event = Event.new(summary="My Event", start=date(2025, 11, 22))
            >>> pprint(event.to_jcal())
            ['vevent',
             [['dtstamp', {}, 'date-time', '2025-05-17T08:06:12Z'],
              ['summary', {}, 'text', 'My Event'],
              ['uid', {}, 'text', 'd755cef5-2311-46ed-a0e1-6733c9e15c63'],
              ['dtstart', {}, 'date', '2025-11-22']],
             []]
        """

        # Iterative tree walk to avoid RecursionError on deeply nested
        # components, mirroring the iterative iCal parser/serializer (GH #1370).
        def make_node(comp: Component) -> list:
            properties = [
                item.to_jcal(key.lower())
                for key, value in comp.items()
                for item in (value if isinstance(value, list) else [value])
            ]
            return [comp.name.lower(), properties, []]

        root_node = make_node(self)
        # stack of (component, jCal node) pairs still to expand
        stack: list[tuple[Component, list]] = [(self, root_node)]
        while stack:
            comp, node = stack.pop()
            children = node[2]
            for subcomponent in comp.subcomponents:
                child_node = make_node(subcomponent)
                children.append(child_node)
                stack.append((subcomponent, child_node))
        return root_node

    def to_json(self) -> str:
        """Return this component as a jCal JSON string.

        Returns:
            JSON string

        See also :attr:`to_jcal`.
        """
        return json.dumps(self.to_jcal())

    @classmethod
    def from_jcal(cls, jcal: str | list) -> Component:
        """Create a component from a jCal list.

        Parameters:
            jcal: jCal list or JSON string according to :rfc:`7265`.

        Raises:
            ~error.JCalParsingError: If the jCal provided is invalid.
            ~json.JSONDecodeError: If the provided string is not valid JSON.

        This reverses :func:`to_json` and :func:`to_jcal`.

        The following code parses an example from :rfc:`7265`:

        .. code-block:: pycon

            >>> from icalendar import Component
            >>> jcal = ["vcalendar",
            ...   [
            ...     ["calscale", {}, "text", "GREGORIAN"],
            ...     ["prodid", {}, "text", "-//Example Inc.//Example Calendar//EN"],
            ...     ["version", {}, "text", "2.0"]
            ...   ],
            ...   [
            ...     ["vevent",
            ...       [
            ...         ["dtstamp", {}, "date-time", "2008-02-05T19:12:24Z"],
            ...         ["dtstart", {}, "date", "2008-10-06"],
            ...         ["summary", {}, "text", "Planning meeting"],
            ...         ["uid", {}, "text", "4088E990AD89CB3DBB484909"]
            ...       ],
            ...       []
            ...     ]
            ...   ]
            ... ]
            >>> calendar = Component.from_jcal(jcal)
            >>> print(calendar.name)
            VCALENDAR
            >>> print(calendar.prodid)
            -//Example Inc.//Example Calendar//EN
            >>> event = calendar.events[0]
            >>> print(event.summary)
            Planning meeting

        """
        if isinstance(jcal, str):
            jcal = json.loads(jcal)
        # Iterative tree build to avoid RecursionError on deeply nested jCal,
        # mirroring the iterative iCal parser (GH #1370). ``_node_from_jcal``
        # parses a single component (without its subcomponents); the stack walks
        # the subcomponent tree, accumulating the jCal error path ([2, i] per
        # nesting level) so error messages match the recursive implementation.
        root, root_subcomponents = _node_from_jcal(jcal, cls)
        stack: list[tuple[Component, list, list]] = [(root, root_subcomponents, [])]
        while stack:
            parent, subcomponents, prefix = stack.pop()
            for i, subcomponent in enumerate(subcomponents):
                child_prefix = [*prefix, 2, i]
                # Prepend the full nesting path so errors match the recursive
                # implementation. This also preserves the error value and
                # traceback, like the nested context managers did before.
                with JCalParsingError.reraise_with_path_added(*child_prefix):
                    child, child_subcomponents = _node_from_jcal(
                        subcomponent, type(parent)
                    )
                parent.subcomponents.append(child)
                stack.append((child, child_subcomponents, child_prefix))
        return root

    def copy(self, recursive: bool = False) -> Self:
        """Copy the component.

        Parameters:
            recursive:
                If ``True``, this creates copies of the component, its subcomponents,
                and all its properties.
                If ``False``, this only creates a shallow copy of the component.

        Returns:
            A copy of the component.

        Examples:

            Create a shallow copy of a component:

            .. code-block:: pycon

                >>> from icalendar import Event
                >>> event = Event.new(description="Event to be copied")
                >>> event_copy = event.copy()
                >>> str(event_copy.description)
                'Event to be copied'

            Shallow copies lose their subcomponents:

            .. code-block:: pycon

                >>> from icalendar import Calendar
                >>> calendar = Calendar.example()
                >>> len(calendar.subcomponents)
                3
                >>> calendar_copy = calendar.copy()
                >>> len(calendar_copy.subcomponents)
                0

            A recursive copy also copies all the subcomponents:

            .. code-block:: pycon

                >>> full_calendar_copy = calendar.copy(recursive=True)
                >>> len(full_calendar_copy.subcomponents)
                3
                >>> full_calendar_copy.events[0] == calendar.events[0]
                True
                >>> full_calendar_copy.events[0] is calendar.events[0]
                False

        """
        if recursive:
            return deepcopy(self)
        return super().copy()

    def is_lazy(self) -> bool:
        """This component is fully parsed."""
        return False

    def parse(self) -> Self:
        """Return the fully parsed component.

        For non-lazy components, this returns self.
        For lazy components, this parses the component and returns the result.
        """
        return self


def _node_from_jcal(jcal, starting_cls: type[Component]) -> tuple[Component, list]:
    """Parse a single jCal component without recursing into subcomponents.

    Module-level helper for :meth:`Component.from_jcal`: it has no ties to a
    class or instance (the relevant class is passed in as ``starting_cls``), so
    it is a plain function rather than a (static) method.

    Parameters:
        jcal: The jCal list for one component.
        starting_cls: The class used as the parser for structural validation
            before the component type is resolved from its name (the entry
            class for the root, the parent's resolved class for a child).

    Returns:
        A ``(component, raw_subcomponents)`` tuple. The raw subcomponents are
        returned for the caller to walk iteratively.

    Raises:
        ~error.JCalParsingError: If this component node is invalid. The path
            is relative to this node; callers prepend the nesting path.
    """
    if not isinstance(jcal, list) or len(jcal) != 3:
        raise JCalParsingError(
            "A component must be a list with 3 items.", starting_cls, value=jcal
        )
    name, properties, subcomponents = jcal
    if not isinstance(name, str):
        raise JCalParsingError(
            "The name must be a string.", starting_cls, path=[0], value=name
        )
    if name.upper() != starting_cls.name:
        # delegate to correct component class
        component_cls = starting_cls.get_component_class(name.upper())
    else:
        component_cls = starting_cls
    component = component_cls()
    if not isinstance(properties, list):
        raise JCalParsingError(
            "The properties must be a list.",
            component_cls,
            path=1,
            value=properties,
        )
    for i, prop in enumerate(properties):
        JCalParsingError.validate_property(prop, component_cls, path=[1, i])
        prop_name = prop[0]
        prop_value = prop[2]
        prop_cls: type[VPROPERTY] = component_cls.types_factory.for_property(
            prop_name, prop_value
        )
        with JCalParsingError.reraise_with_path_added(1, i):
            v_prop = prop_cls.from_jcal(prop)
        # jCal encodes the value type in the type field (``prop[2]``)
        # instead of as a ``VALUE`` parameter (RFC 7265). Restore that
        # parameter when the type differs from the property's default, so
        # explicit value types such as ``RDATE;VALUE=PERIOD`` or
        # ``TRIGGER;VALUE=DATE-TIME`` survive the round-trip (GH #1426).
        # A type equal to the default needs no VALUE parameter, and the
        # reserved ``unknown`` type must never become ``VALUE=UNKNOWN``
        # (RFC 7265, section 5.2).
        default_type = component_cls.types_factory.default_value_type(prop_name)
        if isinstance(prop_value, str) and prop_value.lower() not in (
            "unknown",
            default_type,
        ):
            v_prop.VALUE = prop_value.upper()
        elif "VALUE" in v_prop.params:
            del v_prop.VALUE
        component.add(prop_name, v_prop)
    if not isinstance(subcomponents, list):
        raise JCalParsingError(
            "The subcomponents must be a list.",
            component_cls,
            2,
            value=subcomponents,
        )
    return component, subcomponents


__all__ = ["Component"]
