"""A property must not be declared as both a singleton and multiple.

``Component.singletons`` lists properties that may appear at most once, while
``Component.multiple`` lists properties that may appear more than once. A
property in both lists is contradictory. This guards the whole component
registry against that mistake.

See https://github.com/collective/icalendar/issues/1569
"""

from __future__ import annotations

import pytest

from icalendar import ComponentFactory

COMPONENT_CLASSES = sorted(set(ComponentFactory().values()), key=lambda cls: cls.name)


@pytest.mark.parametrize("component", COMPONENT_CLASSES, ids=lambda cls: cls.name)
def test_singletons_and_multiple_are_disjoint(component):
    """No property is classified as both a singleton and multiple."""
    both = set(component.singletons) & set(component.multiple)
    assert not both, f"{component.name} lists {sorted(both)} in both lists"


def test_alarm_attach_is_multiple_not_singleton():
    """ATTACH may repeat on an email alarm (RFC 5545, 3.6.6), so it is multiple."""
    from icalendar import Alarm

    assert "ATTACH" in Alarm.multiple
    assert "ATTACH" not in Alarm.singletons
