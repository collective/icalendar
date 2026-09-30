"""Fixtures for xcal serialization."""

import pytest

from icalendar import prop
from icalendar.tests.conftest import PROPERTY_NAMES

EXCLUDED_PROPERTY_NAMES = {
    # VCARD
    "vOrg",
    "vAdr",
    "vN",
    # not in use
    "vInline",
}

XCAL_PROPERTY_NAMES = PROPERTY_NAMES - EXCLUDED_PROPERTY_NAMES


@pytest.fixture(params=XCAL_PROPERTY_NAMES)
def xcal_prop_name(request):
    """Names of property types that occur as a property of a component."""
    return request.param


@pytest.fixture
def xcal_prop(xcal_prop_name):
    """Property types that occur as a property of a component."""
    return getattr(prop, xcal_prop_name)


@pytest.fixture
def xcal_prop_example(xcal_prop) -> prop.VPROPERTY:
    return xcal_prop.examples()[0]
