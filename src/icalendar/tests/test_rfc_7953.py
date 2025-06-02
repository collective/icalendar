"""This tests the parsing of the VAVAILABILITY component as defined in :rfc:`7953`."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from icalendar import Availability


def test_uid(availabilities):
    """Test the UID property."""
    availability: Availability = availabilities.rfc_7953_1
    assert availability.uid == "0428C7D2-688E-4D2E-AC52-CD112E2469DF"


def test_organizer(availabilities):
    """Test the ORGANIZER property."""
    availability: Availability = availabilities.rfc_7953_1
    assert availability.organizer == "mailto:bernard@example.com"
    assert availability.organizer.email == "bernard@example.com"


def test_dtstamp(availabilities, tzp):
    """Test the DTSTAMP property."""
    availability: Availability = availabilities.rfc_7953_1
    assert availability.DTSTAMP == tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))


def test_subcomponents(availabilities):
    """Test the subcomponents."""
    availability: Availability = availabilities.rfc_7953_1
    assert len(availability.subcomponents) == 1
    assert availability.available == availability.subcomponents
