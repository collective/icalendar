"""Common functionality."""

import pytest


@pytest.fixture
def link_component(link_component_class):
    """An instance of the component class to test."""
    return link_component_class()


@pytest.fixture(params=[None, "Venue"])
def LABEL(request):
    """The LABEL of the link."""
    return request.param


@pytest.fixture(params=[None, "de", "en-GB"])
def LANGUAGE(request):
    """The LANGUAGE of the link."""
    return request.param


@pytest.fixture(
    params=[None, "SOURCE", "https://example.com/linkrel/derivedFrom", "icon"]
)
def LINKREL(request):
    """The LINKREL of the link."""
    return request.param


@pytest.fixture(params=[None, "de", "en-GB"])
def FMTTYPE(request):
    """The FMTTYPE of the link."""
    return request.param
