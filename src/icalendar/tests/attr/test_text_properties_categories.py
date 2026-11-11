import unicodedata

from icalendar import Event

NFD = "cafe\u0301"
NFC = "caf\u00e9"


def test_summary_is_nfc():
    """Summary returns the NFC form."""
    event = Event.from_ical(f"BEGIN:VEVENT\r\nSUMMARY:{NFD}\r\nEND:VEVENT\r\n")
    assert event.summary == NFC
    assert unicodedata.is_normalized("NFC", event.summary)


def test_round_trip_keeps_original():
    """Serializing back out preserves the original NFD bytes."""
    ics = f"BEGIN:VEVENT\r\nSUMMARY:{NFD}\r\nEND:VEVENT\r\n"
    assert NFD.encode() in Event.from_ical(ics).to_ical()


def test_language_param_is_kept():
    """Normalizing the value must not drop the LANGUAGE parameter."""
    ics = f"BEGIN:VEVENT\r\nSUMMARY;LANGUAGE=fr:{NFD}\r\nEND:VEVENT\r\n"
    assert Event.from_ical(ics).summary.params["LANGUAGE"] == "fr"


def test_uid_is_not_normalized():
    """UID is an identifier, not display text, so it keeps the exact form it was given."""
    ics = f"BEGIN:VEVENT\r\nUID:{NFD}\r\nEND:VEVENT\r\n"
    assert Event.from_ical(ics).uid == NFD


def test_categories_are_nfc():
    """Each item in a CATEGORIES list is normalized independently."""
    ics = f"BEGIN:VEVENT\r\nCATEGORIES:{NFD},Work\r\nEND:VEVENT\r\n"
    assert Event.from_ical(ics).categories == [NFC, "Work"]
