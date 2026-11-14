"""The VLOCATION component from :rfc:`9073#section-7.2`."""

from .component import Component


class Location(Component):
    """A location associated with an event or task.

    Set ``UID`` to identify the location. Optional properties are ``NAME``,
    ``DESCRIPTION``, ``GEO``, and ``LOCATION-TYPE``. A single ``LOCATION-TYPE``
    property can contain several types describing the same location, such as
    a hotel with a restaurant, per :rfc:`9073#section-6.1`.

    Use :meth:`~icalendar.cal.component.Component.add_component` to associate
    multiple locations with an event or task. The :attr:`name` attribute
    identifies the component as ``VLOCATION``; use ``location["NAME"]`` to
    access the location's display name.

    Example:
        Create a location and add it to an event.

        .. code-block:: pycon

            >>> from icalendar import Event, Location
            >>> event = Event()
            >>> location = Location()
            >>> location.add("uid", "hotel@example.com")
            >>> location.add("name", "Central Hotel")
            >>> location.add("geo", (48.2, 16.37))
            >>> location.add("location-type", ["hotel", "restaurant"])
            >>> event.add_component(location)
            >>> str(event.walk("VLOCATION")[0]["NAME"])
            'Central Hotel'
            >>> location["LOCATION-TYPE"].to_ical()
            b'hotel,restaurant'
    """

    name = "VLOCATION"
    required = ("UID",)
    singletons = ("UID", "NAME", "DESCRIPTION", "GEO", "LOCATION-TYPE")


__all__ = ["Location"]
