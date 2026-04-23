"""Tests for Unicode NFC normalization in vText (issue #1311).

See https://github.com/collective/icalendar/issues/1311
"""

import unicodedata

import pytest

from icalendar import Event
from icalendar.prop import vText


class TestUnicodeNFCNormalization:
    """Test that vText normalizes Unicode to NFC form."""

    def test_vtext_normalizes_nfc(self):
        """vText should normalize decomposed characters to NFC."""
        # é as decomposed (e + combining acute)
        decomposed = "caf\u0065\u0301"
        # é as precomposed
        precomposed = "caf\u00e9"
        assert decomposed != precomposed
        assert len(decomposed) == 5  # c-a-f-e-combining_acute
        assert len(precomposed) == 4  # c-a-f-é

        text = vText(decomposed)
        assert str(text) == precomposed
        assert len(str(text)) == 4

    def test_vtext_preserves_already_nfc(self):
        """vText should leave already-NFC text unchanged."""
        nfc_text = "caf\u00e9"
        text = vText(nfc_text)
        assert str(text) == nfc_text

    def test_vtext_normalizes_multiple_chars(self):
        """vText should normalize multiple decomposed characters."""
        decomposed = "na\u0069\u0308ve"  # naïve with decomposed diaeresis
        precomposed = "na\u00efve"
        text = vText(decomposed)
        assert str(text) == precomposed

    def test_vtext_normalizes_from_bytes(self):
        """vText should normalize when created from bytes."""
        decomposed = "caf\u0065\u0301"
        text = vText(decomposed.encode("utf-8"))
        assert str(text) == "caf\u00e9"

    def test_event_summary_normalized(self):
        """Event summary should be NFC-normalized."""
        event = Event()
        event.add("SUMMARY", "caf\u0065\u0301")
        assert str(event["SUMMARY"]) == "caf\u00e9"

    def test_event_description_normalized(self):
        """Event description should be NFC-normalized."""
        event = Event()
        event.add("DESCRIPTION", "na\u0069\u0308ve")
        assert str(event["DESCRIPTION"]) == "na\u00efve"

    def test_event_location_normalized(self):
        """Event location should be NFC-normalized."""
        event = Event()
        event.add("LOCATION", "Z\u0075\u0308rich")
        assert str(event["LOCATION"]) == "Z\u00fcrich"

    def test_vtext_ical_output_consistent(self):
        """Two semantically equivalent texts should serialize identically."""
        decomposed = vText("caf\u0065\u0301")
        precomposed = vText("caf\u00e9")
        assert decomposed.to_ical() == precomposed.to_ical()

    def test_vtext_equality_after_normalization(self):
        """Two vTexts with equivalent Unicode should be equal."""
        decomposed = vText("caf\u0065\u0301")
        precomposed = vText("caf\u00e9")
        assert decomposed == precomposed

    def test_vtext_from_ical_normalizes(self):
        """vText.from_ical should also normalize to NFC."""
        decomposed = "caf\u0065\u0301"
        text = vText.from_ical(decomposed)
        assert str(text) == "caf\u00e9"

    def test_vtext_empty_string(self):
        """vText should handle empty strings."""
        text = vText("")
        assert str(text) == ""

    def test_vtext_ascii_unchanged(self):
        """ASCII text should be unchanged by NFC normalization."""
        ascii_text = "Hello, World!"
        text = vText(ascii_text)
        assert str(text) == ascii_text
