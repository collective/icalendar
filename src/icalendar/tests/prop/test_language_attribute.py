"""Test the language attribute and parameter across icalendar.prop classes.

Related to:
- RFC 5646
- Issue #1890: language attribute for text types
"""

import pytest

from icalendar.prop import (
    vCalAddress,
    vCategory,
    vText,
    vUnknown,
    vUri,
)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: vText("Summary text"),
        lambda: vCategory(["Work", "Meeting"]),
        lambda: vCalAddress("mailto:user@example.com"),
        lambda: vUnknown("custom text value"),
        lambda: vUri("https://example.com/calendar.ics"),
    ],
    ids=["vText", "vCategory", "vCalAddress", "vUnknown", "vUri"],
)
def test_language_attribute_accessors(factory):
    """Test language property: None by default, getter, setter, del, and set to None."""
    prop = factory()

    # 1. Accesses self.params and returns None if no language is set
    assert prop.language is None
    assert prop.LANGUAGE is None
    assert "LANGUAGE" not in prop.params

    # 2. Sets the language string
    prop.language = "en-US"
    assert prop.language == "en-US"
    assert prop.LANGUAGE == "en-US"
    assert prop.params.get("LANGUAGE") == "en-US"

    # 3. Deletes the language param when set to None
    prop.language = None
    assert prop.language is None
    assert prop.LANGUAGE is None
    assert "LANGUAGE" not in prop.params

    # 4. Sets and deletes with `del`
    prop.language = "de-DE"
    assert prop.language == "de-DE"
    del prop.language
    assert prop.language is None
    assert prop.LANGUAGE is None
    assert "LANGUAGE" not in prop.params


@pytest.mark.parametrize(
    ("raw_tag", "expected_standardized"),
    [
        ("en-us", "en-US"),
        ("de_de", "de-DE"),
        ("fr-ca", "fr-CA"),
        ("zh-cmn-hans", "zh-Hans"),
    ],
)
def test_language_standardization_with_langcodes(raw_tag, expected_standardized):
    """Test that langcodes.standardize_tag normalizes tags according to RFC 5646."""
    langcodes = pytest.importorskip("langcodes")
    standardized = langcodes.standardize_tag(raw_tag)
    assert standardized == expected_standardized

    text = vText("International meeting")
    text.language = standardized
    assert text.language == expected_standardized
    assert text.params["LANGUAGE"] == expected_standardized


def test_language_in_ical_serialization():
    """Test that language parameter renders properly in iCalendar output."""
    text = vText("Meeting with team")
    text.language = "en-US"
    assert text.params["LANGUAGE"] == "en-US"

    addr = vCalAddress("mailto:organizer@example.com")
    addr.language = "fr-FR"
    assert addr.params["LANGUAGE"] == "fr-FR"
