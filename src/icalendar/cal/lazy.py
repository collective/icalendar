"""Lazy parsing wrapper for iCalendar property values."""

__all__ = ["LazyProperty"]


class LazyProperty:
    """Defers parsing of property values until first access.

    This wrapper stores the raw iCalendar string and associated metadata,
    only parsing when the value is actually accessed. On parse failure,
    falls back to vText to preserve the raw value.
    """

    __slots__ = (
        "_component",
        "_factory",
        "_params",
        "_parse_error",
        "_parsed_value",
        "_property_name",
        "_raw_value",
        "_tzid",
        "_value_param",
    )

    def __init__(
        self,
        raw_value,
        params,
        property_name,
        factory,
        value_param=None,
        tzid=None,
        component=None,
    ):
        """Initialize lazy property wrapper.

        Args:
            raw_value: Raw iCalendar string value
            params: Parameters object
            property_name: Property name (e.g., 'RRULE')
            factory: TypesFactory instance
            value_param: Optional VALUE parameter
            tzid: Optional TZID for datetime properties
            component: Parent component for error reporting
        """
        self._raw_value = raw_value
        self._params = params
        self._property_name = property_name
        self._factory = factory
        self._value_param = value_param
        self._tzid = tzid
        self._component = component
        self._parsed_value = None
        self._parse_error = None

    @property
    def params(self):
        """Get parameters without triggering parse."""
        return object.__getattribute__(self, "_params")

    @params.setter
    def params(self, value):
        """Set parameters on both wrapper and parsed value."""
        object.__setattr__(self, "_params", value)
        parsed_value = object.__getattribute__(self, "_parsed_value")
        if parsed_value is not None:
            parsed_value.params = value

    def _ensure_parsed(self):
        """Parse the value if not already parsed."""
        # Access _parsed_value using object.__getattribute__
        # to avoid __getattr__ recursion
        if object.__getattribute__(self, "_parsed_value") is not None:
            return

        raw_value = object.__getattribute__(self, "_raw_value")
        params = object.__getattribute__(self, "_params")
        property_name = object.__getattribute__(self, "_property_name")
        factory = object.__getattribute__(self, "_factory")
        value_param = object.__getattribute__(self, "_value_param")
        tzid = object.__getattribute__(self, "_tzid")
        component = object.__getattribute__(self, "_component")

        factory_class = factory.for_property(property_name, value_param)

        try:
            if tzid:
                parsed = factory_class.from_ical(raw_value, tzid)
            else:
                parsed = factory_class.from_ical(raw_value)

            parsed_value = factory_class(parsed)
            parsed_value.params = params
            object.__setattr__(self, "_parsed_value", parsed_value)

        except (ValueError, TypeError) as e:
            # Fall back to vText for unparseable values
            parse_error = str(e)
            vtext_factory = factory["text"]
            parsed_value = vtext_factory(raw_value)
            parsed_value.params = params
            object.__setattr__(self, "_parsed_value", parsed_value)
            object.__setattr__(self, "_parse_error", parse_error)

            if component is not None:
                component.errors.append((property_name, parse_error))

    def get_parsed_value(self):
        """Get the parsed value, parsing if necessary."""
        self._ensure_parsed()
        return object.__getattribute__(self, "_parsed_value")

    def __getattr__(self, name):
        """Delegate attribute access to parsed value."""
        return getattr(self.get_parsed_value(), name)

    def __repr__(self):
        """Return repr of parsed value or lazy repr."""
        parsed_value = object.__getattribute__(self, "_parsed_value")
        if parsed_value is not None:
            return repr(parsed_value)
        property_name = object.__getattribute__(self, "_property_name")
        raw_value = object.__getattribute__(self, "_raw_value")
        return f"LazyProperty({property_name}={raw_value!r})"

    def __str__(self):
        """Return string representation of parsed value."""
        return str(self.get_parsed_value())

    def __eq__(self, other):
        """Delegate equality to parsed value."""
        # Handle comparison with another LazyProperty
        if isinstance(other, LazyProperty):
            return self.get_parsed_value() == other.get_parsed_value()
        return self.get_parsed_value() == other

    def __ne__(self, other):
        """Delegate inequality to parsed value."""
        # Handle comparison with another LazyProperty
        if isinstance(other, LazyProperty):
            return self.get_parsed_value() != other.get_parsed_value()
        return self.get_parsed_value() != other

    def __hash__(self):
        """Delegate hashing to parsed value."""
        return hash(self.get_parsed_value())

    def to_ical(self):
        """Convert to iCalendar format."""
        return self.get_parsed_value().to_ical()

    def to_jcal(self, *args, **kwargs):
        """Convert to jCal (JSON) format."""
        return self.get_parsed_value().to_jcal(*args, **kwargs)
