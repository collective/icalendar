"""This tests the parsing of the VAVAILABILITY component as defined in :rfc:`7953`."""

from datetime import date, datetime, timedelta

import pytest

from icalendar import BUSYTYPE, Availability, Available
from icalendar.error import IncompleteComponent


@pytest.fixture(params=[Availability, Available])
def rfc_7953_component_class(request):
    """The component class."""
    return request.param


@pytest.fixture
def rfc_7953_component(rfc_7953_component_class):
    """The component class."""
    return rfc_7953_component_class()


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


def test_busy_type_default():
    assert Availability().busy_type == BUSYTYPE.BUSY_UNAVAILABLE


def test_set_busy_type():
    availability = Availability()
    availability.busy_type = BUSYTYPE.BUSY
    assert availability.busy_type == BUSYTYPE.BUSY
    assert availability["BUSYTYPE"] == "BUSY"


def test_new_sets_default(test_uid):
    availability = Availability.new()
    assert availability.busy_type == BUSYTYPE.BUSY_UNAVAILABLE
    assert availability.uid == test_uid


def test_create_new_availability_with_subsomponents(dont_validate_new):
    avaiable = Available.new(summary="Available1")
    availability = Availability.new(busy_type=BUSYTYPE.BUSY, components=[avaiable])
    assert len(availability.available) == 1
    assert availability.available[0].summary == "Available1"


def test_avaiable_needs_start():
    """Start is required and not set automatically"""
    with pytest.raises(ValueError) as e:
        Available.new()
    assert "Available start must be a datetime with a timezone" in str(e.value)


@pytest.mark.parametrize("key", ["start", "end"])
@pytest.mark.parametrize(
    "value", [datetime(2011, 10, 5, 13, 32, 25), date(2011, 10, 5)]
)
def test_avaiable_needs_timezone(key, value, rfc_7953_component_class):
    """Start is required and not set automatically"""
    kw = {key: value}
    with pytest.raises(ValueError) as e:
        rfc_7953_component_class.new(**kw)
    assert f"{key} must be a datetime with a timezone" in str(e.value)


def test_create_with_start(tzp):
    """Create with a valid start."""
    start = tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))
    available = Available.new(start=start)
    assert available.start == start


def test_create_with_start_and_end(tzp):
    """Create with a valid start and end."""
    start = tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))
    end = tzp.localize_utc(datetime(2011, 10, 5, 14, 32, 25))
    available = Available.new(start=start, end=end)
    assert available.start == start
    assert available.end == end


def test_duration_from_end(rfc_7953_component, tzp):
    """Check the computation of end and duration."""
    rfc_7953_component.start = tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))
    rfc_7953_component.end = tzp.localize_utc(datetime(2011, 10, 5, 14, 32, 25))
    assert rfc_7953_component.duration == timedelta(hours=1)


def test_duration_and_end_from_duration(rfc_7953_component, tzp):
    """Check the computation of end and duration."""
    rfc_7953_component.start = tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))
    rfc_7953_component.DURATION = timedelta(hours=1)
    assert rfc_7953_component.duration == timedelta(hours=1)
    assert rfc_7953_component.end == tzp.localize_utc(datetime(2011, 10, 5, 14, 32, 25))


def test_start_only_has_no_duration(rfc_7953_component, tzp):
    """Check the computation of end and duration."""
    rfc_7953_component.start = tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))
    assert rfc_7953_component.duration is None
    assert rfc_7953_component.end is None


def test_missing_info_for_end(rfc_7953_component):
    """We miss information and cannot compute the end."""
    rfc_7953_component.DURATION = timedelta(hours=1)
    with pytest.raises(IncompleteComponent) as e:
        rfc_7953_component.end  # noqa: B018
    assert "Cannot compute end without start" in str(e.value)


def test_missing_info_for_duration(rfc_7953_component, tzp):
    """We only have a duration."""
    rfc_7953_component.end = tzp.localize_utc(datetime(2011, 10, 5, 13, 32, 25))
    with pytest.raises(IncompleteComponent) as e:
        rfc_7953_component.duration  # noqa: B018
    assert "Cannot compute duration without start" in str(e.value)
