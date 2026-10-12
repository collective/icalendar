"""Tests for the attachments property on ATTACH-supporting components."""

from __future__ import annotations

from datetime import timedelta

import pytest

from icalendar import Alarm, Event, Journal, Todo
from icalendar.error import InvalidCalendar
from icalendar.prop import vBinary, vUri

ComponentWithAttachments = Alarm | Event | Journal | Todo


@pytest.fixture(params=[Alarm, Event, Journal, Todo])
def component(request) -> ComponentWithAttachments:
    """Return a component that supports ATTACH."""
    return request.param()


def test_absent_attachments_returns_empty_list(component):
    """An absent property returns [] without inserting ATTACH."""
    assert component.attachments == []
    assert "ATTACH" not in component


def test_string_becomes_vuri(component):
    """A string becomes vUri."""
    component.attachments = "https://example.com/file.pdf"
    assert len(component.attachments) == 1
    assert isinstance(component.attachments[0], vUri)
    assert component.attachments[0] == "https://example.com/file.pdf"


def test_bytes_become_vbinary(component):
    """Bytes, including non-UTF-8 bytes, become vBinary."""
    payload = b"\xff\xfe\x00binary"
    component.attachments = payload
    assert len(component.attachments) == 1
    attachment = component.attachments[0]
    assert isinstance(attachment, vBinary)
    assert attachment.bytes == payload


def test_binary_serialization_includes_encoding_and_value(component):
    """Binary serialization includes VALUE=BINARY, ENCODING=BASE64, and payload."""
    component.attachments = b"hello"
    ical = component.to_ical().decode()
    assert "VALUE=BINARY" in ical
    assert "ENCODING=BASE64" in ical
    assert "aGVsbG8=" in ical


def test_typed_values_preserve_parameters(component):
    """Existing vUri and vBinary parameters remain intact."""
    uri = vUri(
        "https://example.com/agenda.pdf",
        params={"FMTTYPE": "application/pdf"},
    )
    binary = vBinary(b"data", params={"FMTTYPE": "application/octet-stream"})
    component.attachments = [uri, binary]
    got_uri, got_binary = component.attachments
    assert got_uri.params["FMTTYPE"] == "application/pdf"
    assert got_binary.params["FMTTYPE"] == "application/octet-stream"
    assert got_binary.params["VALUE"] == "BINARY"
    assert got_binary.params["ENCODING"] == "BASE64"


def test_mixed_list_preserves_order(component):
    """Mixed URI and binary lists preserve their order."""
    component.attachments = [
        "https://example.com/a.pdf",
        b"bytes-a",
        "https://example.com/b.pdf",
        b"bytes-b",
    ]
    values = component.attachments
    assert isinstance(values[0], vUri)
    assert isinstance(values[1], vBinary)
    assert isinstance(values[2], vUri)
    assert isinstance(values[3], vBinary)
    assert values[0] == "https://example.com/a.pdf"
    assert values[1].bytes == b"bytes-a"
    assert values[2] == "https://example.com/b.pdf"
    assert values[3].bytes == b"bytes-b"


def test_second_assignment_replaces(component):
    """A second assignment replaces rather than accumulates."""
    component.attachments = "https://example.com/old.pdf"
    component.attachments = "https://example.com/new.pdf"
    assert component.attachments == [vUri("https://example.com/new.pdf")]


@pytest.mark.parametrize("bad", [1, object(), {"uri": "x"}])
def test_unsupported_types_raise_type_error_without_change(component, bad):
    """Unsupported types raise TypeError without changing attachments."""
    component.attachments = "https://example.com/keep.pdf"
    before = component.to_ical()
    with pytest.raises(TypeError):
        component.attachments = bad
    assert component.to_ical() == before


def test_unsupported_list_item_raises_without_change(component):
    """An unsupported list item raises TypeError without changing attachments."""
    component.attachments = "https://example.com/keep.pdf"
    before = component.to_ical()
    with pytest.raises(TypeError):
        component.attachments = ["https://example.com/ok.pdf", 123]
    assert component.to_ical() == before


@pytest.mark.parametrize("empty", [[], None])
def test_set_empty_clears_attachments(component, empty):
    """Setting an empty list or None removes all attachments."""
    component.attachments = "https://example.com/keep.pdf"
    component.attachments = empty
    assert component.attachments == []
    assert "ATTACH" not in component


def test_del_attachments(component):
    """Deleting the property removes the ATTACH property."""
    component.attachments = "https://example.com/keep.pdf"
    del component.attachments
    assert component.attachments == []
    assert "ATTACH" not in component


def test_set_attachments_round_trips(component):
    """Assigning the property its own value leaves it unchanged."""
    component.attachments = [
        vUri("https://example.com/a.pdf", params={"FMTTYPE": "application/pdf"}),
        vBinary(b"bytes-a"),
    ]
    before = component.to_ical()
    component.attachments = component.attachments
    assert component.to_ical() == before


def test_invalid_uri_leaves_previous_attachments_unchanged(component):
    """Invalid URI input leaves the previous attachments unchanged."""
    component.attachments = "https://example.com/keep.pdf"
    before = component.to_ical()
    with pytest.raises(ValueError, match="CR or LF"):
        component.attachments = "https://example.com/bad\n.pdf"
    assert component.to_ical() == before


def test_parse_serialize_round_trip_preserves_both_types(component):
    """Parse/serialize round trips preserve both attachment types."""
    component.attachments = [
        vUri(
            "https://example.com/agenda.pdf",
            params={"FMTTYPE": "application/pdf"},
        ),
        vBinary(b"\xff\x00data"),
    ]
    restored = type(component).from_ical(component.to_ical())
    assert len(restored.attachments) == 2
    assert isinstance(restored.attachments[0], vUri)
    assert restored.attachments[0] == "https://example.com/agenda.pdf"
    assert restored.attachments[0].params.get("FMTTYPE") == "application/pdf"
    assert isinstance(restored.attachments[1], vBinary)
    assert restored.attachments[1].bytes == b"\xff\x00data"


def test_audio_alarm_rejects_multiple_attachments():
    """Setter raises InvalidCalendar when >1 attachment is given and ACTION is AUDIO."""
    alarm = Alarm.new_audio(timedelta(minutes=-5))
    with pytest.raises(InvalidCalendar, match="AUDIO"):
        alarm.attachments = [
            "ftp://example.com/sound1.aud",
            "ftp://example.com/sound2.aud",
        ]


def test_audio_alarm_rejects_multiple_attachments_error_message():
    """Error message names the constraint and includes the actual count."""
    alarm = Alarm.new_audio(timedelta(minutes=-5))
    attachments = [
        "ftp://example.com/sound1.aud",
        "ftp://example.com/sound2.aud",
    ]
    with pytest.raises(InvalidCalendar) as exc_info:
        alarm.attachments = attachments
    msg = str(exc_info.value)
    assert "must not contain more than one attachment" in msg
    assert f"Alarm has {len(attachments)} attachments" in msg


def test_audio_alarm_accepts_single_attachment():
    """A single attachment is valid for an AUDIO alarm."""
    alarm = Alarm.new_audio(timedelta(minutes=-5))
    alarm.attachments = "ftp://example.com/sound.aud"
    assert len(alarm.attachments) == 1


def test_audio_alarm_accepts_zero_attachments():
    """An AUDIO alarm accepts zero attachments without raising."""
    alarm = Alarm.new_audio(timedelta(minutes=-5))
    alarm.attachments = None
    assert alarm.attachments == []
    alarm.attachments = []
    assert alarm.attachments == []


def test_new_with_audio_action_rejects_multiple_attachments():
    """Alarm.new() enforces AUDIO cardinality when action='AUDIO' is given."""
    with pytest.raises(
        InvalidCalendar, match="must not contain more than one attachment"
    ):
        Alarm.new(
            action="AUDIO",
            attachments=[
                "ftp://example.com/sound1.aud",
                "ftp://example.com/sound2.aud",
            ],
        )


def test_setting_audio_action_on_alarm_with_multiple_attachments_raises():
    alarm = Alarm.new(attachments=["ftp://a.com/a.aud", "ftp://b.com/b.aud"])
    with pytest.raises(
        InvalidCalendar, match="must not contain more than one attachment"
    ):
        alarm.ACTION = "AUDIO"
