"""Test the language attribute and parameter across icalendar.prop classes.

Related to:
- RFC 5646
- Issue #1890: language attribute for text types
"""

import pytest

from icalendar.cal import Event
from icalendar.prop import (
    vCalAddress,
    vCategory,
    vText,
    vUnknown,
    vUri,
)


@pytest.fixture(
    params=[
        lambda: vText("Summary text"),
        lambda: vCategory(["Work", "Meeting"]),
        lambda: vCalAddress("mailto:user@example.com"),
        lambda: vUnknown("custom text value"),
        lambda: vUri("https://example.com/calendar.ics"),
    ],
    ids=["vText", "vCategory", "vCalAddress", "vUnknown", "vUri"],
)
def prop(request):
    return request.param()


def test_no_language_is_none(prop):
    """Accesses self.params and returns None if no language is set."""
    assert prop.language is None
    assert prop.LANGUAGE is None
    assert "LANGUAGE" not in prop.params


def test_set_language(prop):
    """Sets the language string."""
    prop.language = "en-US"
    assert prop.language == "en-US"
    assert prop.LANGUAGE == "en-US"
    assert prop.params.get("LANGUAGE") == "en-US"


def test_delete_language_when_none(prop):
    """Deletes the language param when set to None."""
    prop.language = "en-US"
    prop.language = None
    assert prop.language is None
    assert prop.LANGUAGE is None
    assert "LANGUAGE" not in prop.params


def test_delete_language_with_del(prop):
    """Sets and deletes with del."""
    prop.language = "de-DE"
    assert prop.language == "de-DE"
    del prop.language
    assert prop.language is None
    assert prop.LANGUAGE is None
    assert "LANGUAGE" not in prop.params


def test_invalid_language_raises_value_error(prop):
    """Raises ValueError on setting invalid characters."""
    with pytest.raises(
        ValueError, match="Invalid characters or format in language tag"
    ):
        prop.language = "en\nUS"

    with pytest.raises(
        ValueError, match="Invalid characters or format in language tag"
    ):
        prop.language = "en US"

    with pytest.raises(
        ValueError, match="Invalid characters or format in language tag"
    ):
        prop.language = "en;q=0.8"

    with pytest.raises(
        ValueError, match="Invalid characters or format in language tag"
    ):
        prop.language = "-invalid"


def test_getter_sanitizes_invalid_characters(prop):
    """Getter sanitizes any raw invalid characters from params."""
    prop.params["LANGUAGE"] = "en\r\n-US;invalid"
    assert prop.language == "en-USinvalid"


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

    event = Event()
    event.add("summary", "International meeting")
    event["summary"].language = standardized
    assert event["summary"].language == expected_standardized
    assert event["summary"].params["LANGUAGE"] == expected_standardized

    ical_output = event.to_ical().decode("utf-8")
    assert (
        f"SUMMARY;LANGUAGE={expected_standardized}:International meeting" in ical_output
    )

    parsed_event = Event.from_ical(ical_output)
    assert parsed_event["summary"].language == expected_standardized


def test_language_in_ical_serialization_and_roundtrip():
    """Test that language parameter renders in to_ical output and roundtrips with from_ical."""
    event = Event()
    event.add("summary", "Meeting with team")
    event["summary"].language = "en-US"

    event.add("organizer", "mailto:organizer@example.com")
    event["organizer"].language = "fr-FR"

    event.add("categories", ["Work", "Design"])
    event["categories"].language = "de-DE"

    ical_bytes = event.to_ical()
    ical_text = ical_bytes.decode("utf-8")

    assert "SUMMARY;LANGUAGE=en-US:Meeting with team" in ical_text
    assert "ORGANIZER;LANGUAGE=fr-FR:mailto:organizer@example.com" in ical_text
    assert "CATEGORIES;LANGUAGE=de-DE:Work,Design" in ical_text

    parsed_event = Event.from_ical(ical_bytes)
    assert parsed_event["summary"].language == "en-US"
    assert parsed_event["organizer"].language == "fr-FR"
    assert parsed_event["categories"].language == "de-DE"
