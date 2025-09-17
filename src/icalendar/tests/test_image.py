"""Test the image class to convert from and to binary data."""

import pytest


@pytest.fixture
def images(calendars):
    """Return the images we get from the example calendars."""
