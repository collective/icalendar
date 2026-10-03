"""Additional parsing tests."""

from pathlib import Path

from icalendar.cal.calendar import Calendar
from icalendar.prop.text import vText


def test_parsed_properties_are_not_a_list_if_they_have_one_value(calendars):
    """Test failure in test_equality: some properties are a list."""
    calendar: Calendar = calendars.rfc_7265_appendix_example_1_xcal
    for compoment in calendar.walk():
        for name, value in compoment.items():
            if isinstance(value, list):
                assert len(value) != 1, (
                    f"Property {name} in {compoment.name} should not be a list with one value: {value}"
                )


def test_empty_components(calendars):
    """Empty components tag."""
    calendar = calendars.rfc_6321_special_case
    assert not calendar.subcomponents


def test_empty_property(calendars):
    """Empty property tag should vanish."""
    calendar = calendars.rfc_6321_special_case
    assert "version" not in calendar


def test_empty_parameter(calendars):
    """Empty property tag should vanish."""
    calendar = calendars.rfc_6321_special_case
    x_prop = calendar["x-prop"]
    assert isinstance(x_prop, vText)
    assert x_prop.ical_value == "lalala"
    print(x_prop.params)
    assert "x-param" not in x_prop.params
    assert x_prop.params["x-param-2"] == "test"


def test_from_xcal_takes_path_argument(calendars):
    """Test that from_xcal can take a path argument."""
    cal = calendars.rfc_7265_appendix_example_1_xcal
    path = cal.source_path
    assert isinstance(path, Path)
    cal_parsed = Calendar.from_xcal(path)[0]
    assert cal_parsed == cal
