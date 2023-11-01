"""Test the equality and inequality of components."""
import copy
import pytz


def test_parsed_calendars_are_equal(ics_file):
    """Ensure that a calendar equals the same calendar."""
    copy_of_calendar = ics_file.__class__.from_ical(ics_file.to_ical())
    assert copy_of_calendar == ics_file
    assert not copy_of_calendar != ics_file


def test_copies_are_equal(ics_file):
    """Ensure that copies are equal."""
    assert ics_file.copy() == ics_file.copy()
    assert ics_file.copy() == ics_file
    assert not ics_file.copy() != ics_file.copy()
    assert not ics_file.copy() != ics_file

def test_deep_copies_are_equal(ics_file):
    """Ensure that deep copies are equal."""
    try:
        assert copy.deepcopy(ics_file) == copy.deepcopy(ics_file)
        assert copy.deepcopy(ics_file) == ics_file
        assert not copy.deepcopy(ics_file) != copy.deepcopy(ics_file)
        assert not copy.deepcopy(ics_file) != ics_file
    except pytz.UnknownTimeZoneError:
        # Ignore errors when a custom time zone is used.
        # This is still covered by the parsing test.
        pass


def test_a_components_copy_also_copies_subcomponents(calendars):
    """A calendar's copy does not have the identical subcompoenets!

    We expect to be able to modify a copy but not its values.
    """
    cal = calendars.timezoned
    copy = cal.copy()
    assert copy is not cal
    assert copy.subcomponents
    assert copy.subcomponents is not cal.subcomponents
    assert copy.subcomponents == cal.subcomponents
