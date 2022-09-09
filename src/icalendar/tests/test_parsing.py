import pytest
from icalendar import Calendar

def test_raises_value_error_for_properties_without_parent_pull_179():
        '''Found an issue where from_ical() would raise IndexError for
        properties without parent components.

        https://github.com/collective/icalendar/pull/179
        '''
        with pytest.raises(ValueError):
            Calendar.from_ical('VERSION:2.0')

