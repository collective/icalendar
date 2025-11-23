"""Shared data between tests."""

from icalendar import prop

PROPERTY_NAMES = {attr for attr in dir(prop) if attr[0] == "v" and attr[1].isupper()}
# remove values for now that are in parameters only
PARAMETER_NAMES = {"vSkip", "vWeekday", "vFrequency", "vMonth", "vInline"}
PROPERTY_NAMES -= PARAMETER_NAMES


__all__ = ["PARAMETER_NAMES", "PROPERTY_NAMES"]
