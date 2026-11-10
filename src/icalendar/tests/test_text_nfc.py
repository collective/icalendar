"""Tests for Unicode NFC normalization helpers in icalendar.prop.text.

These test the functions in isolation. Tests that go through real
components (Event, Calendar) live in tests/attr/test_text_properties_nfc.py.
"""

import unicodedata
import pytest

from icalendar.prop import vText
from icalendar.prop.text import to_nfc, to_nfc_list

# Escapes are used on purpose: an editor could silently normalize literal
# characters and make these tests meaningless.
NFD = "cafe\u0301"  # e + combining acute accent
NFC = "caf\u00e9"  # precomposed é


def test_fixtures_really_differ():
    """Guard against an editor or tool silently normalizing this file."""
    assert NFD != NFC
    assert unicodedata.normalize("NFC", NFD) == NFC


# --- to_nfc -----------------------------------------------------------------


def test_to_nfc_converts_nfd_str():
    assert to_nfc(NFD) == NFC


def test_to_nfc_result_is_nfc():
    assert unicodedata.is_normalized("NFC", to_nfc(NFD))


def test_to_nfc_returns_same_object_when_already_nfc():
    assert to_nfc(NFC) is NFC


@pytest.mark.parametrize("value", [None, 1, 1.5, b"abc", ["a"]])
def test_to_nfc_passes_non_str_through(value):
    assert to_nfc(value) is value


def test_to_nfc_empty_string():
    assert to_nfc("") == ""


def test_to_nfc_keeps_vtext_type_params_and_encoding():
    text = vText(NFD, "utf-8", params={"LANGUAGE": "fr"})
    result = to_nfc(text)
    assert isinstance(result, vText)
    assert result == NFC
    assert result.params["LANGUAGE"] == "fr"
    assert result.encoding == "utf-8"


def test_to_nfc_vtext_already_nfc_is_same_object():
    text = vText(NFC)
    assert to_nfc(text) is text


@pytest.mark.parametrize("value", ["\ufb01", "\u2460", "\uff21"])
def test_to_nfc_does_not_apply_compatibility_mappings(value):
    """The fi ligature, circled 1 and full-width A must stay (that is NFKC)."""
    assert to_nfc(value) == value


def test_to_nfc_leaves_combining_sequences_without_composed_form():
    value = "q\u0301"  # no precomposed form exists
    assert to_nfc(value) == value


def test_to_nfc_does_not_touch_whitespace_or_case():
    value = "  Caf\u00e9 \n"
    assert to_nfc(value) == value


# --- to_nfc_list ------------------------------------------------------------


def test_to_nfc_list_empty():
    values = []
    assert to_nfc_list(values) is values


def test_to_nfc_list_returns_same_list_if_nothing_changes():
    values = [NFC, "Work"]
    assert to_nfc_list(values) is values


def test_to_nfc_list_normalizes_each_item():
    assert to_nfc_list([NFD, "Work", NFD]) == [NFC, "Work", NFC]


def test_to_nfc_list_does_not_mutate_input():
    values = [NFD]
    to_nfc_list(values)
    assert values == [NFD]


def test_to_nfc_list_keeps_vtext_params():
    values = [vText(NFD, params={"LANGUAGE": "fr"})]
    result = to_nfc_list(values)
    assert result == [NFC]
    assert result[0].params["LANGUAGE"] == "fr"
