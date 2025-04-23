"""Attributes of Components and properties."""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from icalendar.error import InvalidCalendar
from icalendar.prop import vDDDTypes, vText
from icalendar.timezone import tzp

if TYPE_CHECKING:
    from icalendar.cal import Component


def multi_language_text_property(main_prop:str, compatibility_prop:str, doc:str) -> property:
    """This creates a text property.

    This property can be defined several times with different ``LANGUAGE`` parameters.

    Args:

        main_prop: The property to set and get, such as ``NAME``
        compatibility_prop: An old property used before, such as ``X-WR-CALNAME``
        doc: The documentation string
    """
    def fget(self: Component) -> Optional[str]:
        """Get the property"""
        result = self.get(main_prop, self.get(compatibility_prop))
        if isinstance(result, list):
            for item in result:
                if "LANGUAGE" not in item.params:
                    return item
        return result

    def fset(self: Component, value:str):
        """Set the property."""
        fdel(self)
        self.add(main_prop, value)

    def fdel(self: Component):
        """Delete the property."""
        self.pop(main_prop, None)
        self.pop(compatibility_prop, None)

    return property(fget, fset, fdel, doc)


def single_int_property(prop:str, default:int, doc:str) -> property:
    """Create a property for an int value that exists only once.

    Args:

        prop: The name of the property
        default: The default value
        doc: The documentation string
    """
    def fget(self: Component) -> int:
        """Get the property"""
        try:
            return int(self.get(prop, default))
        except ValueError as e:
            raise InvalidCalendar(f"{prop} must be an int") from e

    def fset(self: Component, value:int):
        """Set the property."""
        fdel(self)
        self.add(prop, value)

    def fdel(self: Component):
        """Delete the property."""
        self.pop(prop, None)

    return property(fget, fset, fdel, doc)


def single_utc_property(name: str, docs: str) -> property:
    """Create a property to access a value of datetime in UTC timezone.

    name - name of the property
    docs - documentation string
    """
    docs = (
        f"""The {name} property. datetime in UTC

    All values will be converted to a datetime in UTC.
    """
        + docs
    )

    def fget(self: Component) -> Optional[datetime]:
        """Get the value."""
        if name not in self:
            return None
        dt = self.get(name)
        if isinstance(dt, vText):
            # we might be in an attribute that is not typed
            value = vDDDTypes.from_ical(dt)
        else:
            value = getattr(dt, "dt", None)
        if value is None or not isinstance(value, date):
            raise InvalidCalendar(f"{name} must be a datetime in UTC, not {value}")
        return tzp.localize_utc(value)

    def fset(self: Component, value: datetime):
        """Set the value"""
        if not isinstance(value, date):
            raise TypeError(f"{name} takes a datetime in UTC, not {value}")
        fdel(self)
        self.add(name, tzp.localize_utc(value))

    def fdel(self: Component):
        """Delete the property."""
        self.pop(name, None)

    return property(fget, fset, fdel, doc=docs)


def single_string_property(name: str, docs: str, other_name:Optional[str]=None) -> property:
    """Create a property to access a single string value."""

    def fget(self: Component) -> str:
        """Get the value."""
        result = self.get(name, None if other_name is None else self.get(other_name, None))
        if result is None or result == []:
            return ""
        if isinstance(result, list):
            return result[0]
        return result

    def fset(self: Component, value: str):
        """Set the value"""
        fdel(self)
        self.add(name, value)

    def fdel(self: Component):
        """Delete the property."""
        self.pop(name, None)
        if other_name is not None:
            self.pop(other_name, None)

    return property(fget, fset, fdel, doc=docs)

color_property = single_string_property(
    "COLOR",
    """This property specifies a color used for displaying the component.

    This implements :rfc:`7986` ``COLOR`` property.

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

    Example: ``"turquoise"``, ``"#ffffff"``

    >>> from icalendar import Todo
    >>> todo = Todo()
    >>> todo.color = "green"
    >>> print(todo.to_ical())
    BEGIN:VTODO
    COLOR:green
    END:VTODO
    """
)

sequence_property = single_int_property(
    "SEQUENCE",
    0,
    """This property defines the revision sequence number of the calendar component within a sequence of revisions.

Value Type:

    INTEGER

Property Parameters:

    IANA and non-standard property parameters can be specified on this property.

Conformance:

    The property can be specified in "VEVENT", "VTODO", or
    "VJOURNAL" calendar component.

Description:

    When a calendar component is created, its sequence
    number is 0.  It is monotonically incremented by the "Organizer's"
    CUA each time the "Organizer" makes a significant revision to the
    calendar component.

    The "Organizer" includes this property in an iCalendar object that
    it sends to an "Attendee" to specify the current version of the
    calendar component.

    The "Attendee" includes this property in an iCalendar object that
    it sends to the "Organizer" to specify the version of the calendar
    component to which the "Attendee" is referring.

    A change to the sequence number is not the mechanism that an
    "Organizer" uses to request a response from the "Attendees".  The
    "RSVP" parameter on the "ATTENDEE" property is used by the
    "Organizer" to indicate that a response from the "Attendees" is
    requested.

    Recurrence instances of a recurring component MAY have different
    sequence numbers.

Examples:

    The following is an example of this property for a calendar
    component that was just created by the "Organizer":

    >>> from icalendar import Event
    >>> event = Event()
    >>> event.sequence
    0

    The following is an example of this property for a calendar
    component that has been revised 10 different times by the
    "Organizer":

    >>> from icalendar import Calendar
    >>> calendar = Calendar.example("issue_156_RDATE_with_PERIOD_TZID_khal")
    >>> event = calendar.events[0]
    >>> event.sequence
    10
    """
)

__all__ = [
    "single_utc_property",
    "color_property",
    "multi_language_text_property",
    "single_int_property",
    "sequence_property"
]
