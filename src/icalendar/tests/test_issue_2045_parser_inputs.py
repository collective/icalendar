"""Consistent serialized input and file ownership for component parsers."""

import codecs
from io import BytesIO, StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import get_type_hints
from xml.etree.ElementTree import ParseError

import pytest

from icalendar import Calendar, Component, Event, config
from icalendar.cal.component import SERIALIZED_INPUT
from icalendar.cal.component_factory import ComponentFactory

PARSER_CLASSES = (Component, Calendar)
FORMATS = ("ical", "jcal", "xcal")
STREAM_KINDS = ("text", "binary")
INPUT_KINDS = ("str", "bytes", "Path", *STREAM_KINDS)
STREAM_PREFIX = "ignored data before the current stream position"


@pytest.fixture
def calendar():
    """A small calendar with non-ASCII text in every serialized format."""
    calendar = Calendar()
    calendar.add("prodid", "-//Parser input tests//EN")
    calendar.add("version", "2.0")
    event = Event()
    event.add("uid", "parser-inputs")
    event.add("summary", "Café ☕")
    calendar.add_component(event)
    return calendar


def serialized(calendar, format_name):
    """Return serialized bytes without bypassing the public writers."""
    if format_name == "ical":
        return calendar.to_ical()
    if format_name == "jcal":
        return calendar.to_json().encode()
    if format_name == "xcal":
        return calendar.to_xcal()
    raise ValueError(f"Unexpected format: {format_name}")


def parse(cls, format_name, data):
    """Normalize only the existing xCal list return type for assertions."""
    result = getattr(cls, f"from_{format_name}")(data)
    return result[0] if format_name == "xcal" else result


def input_data(data, kind, tmp_path):
    """Make one input and position streams just before the calendar data."""
    if kind == "str":
        return data.decode()
    if kind == "bytes":
        return data
    if kind == "Path":
        path = tmp_path / "calendar.data"
        path.write_bytes(data)
        return path
    if kind == "text":
        stream = StringIO(STREAM_PREFIX + data.decode())
    elif kind == "binary":
        stream = BytesIO(STREAM_PREFIX.encode() + data)
    else:
        raise ValueError(f"Unexpected input kind: {kind}")
    # A parser must read from the current position instead of rewinding.
    stream.seek(len(STREAM_PREFIX))
    return stream


@pytest.mark.parametrize("cls", PARSER_CLASSES)
@pytest.mark.parametrize("format_name", FORMATS)
@pytest.mark.parametrize("kind", INPUT_KINDS)
def test_serialized_inputs(cls, format_name, kind, calendar, tmp_path):
    """All parsers accept data, paths and open files, preserving stream ownership."""
    source = input_data(serialized(calendar, format_name), kind, tmp_path)

    result = parse(cls, format_name, source)

    assert isinstance(result, Calendar)
    assert result.to_ical() == calendar.to_ical()
    if kind in STREAM_KINDS:
        assert not source.closed
        assert source.read() == ("" if kind == "text" else b"")


@pytest.mark.parametrize("format_name", FORMATS)
@pytest.mark.parametrize("mode", ["r", "rb"])
def test_open_file(format_name, mode, calendar, tmp_path):
    """Real text and binary files retain their current position and ownership."""
    path = tmp_path / "calendar.data"
    path.write_bytes(STREAM_PREFIX.encode() + serialized(calendar, format_name))
    kwargs = {"encoding": "utf-8"} if mode == "r" else {}
    with path.open(mode, **kwargs) as file:
        file.seek(len(STREAM_PREFIX))

        assert parse(Calendar, format_name, file) == calendar
        assert not file.closed


@pytest.mark.parametrize("cls", PARSER_CLASSES)
def test_ical_input_annotation(cls):
    """The public parser input annotation can be inspected at runtime."""
    assert get_type_hints(cls.from_ical)["st"] == SERIALIZED_INPUT


@pytest.mark.parametrize("cls", PARSER_CLASSES)
def test_native_jcal_list(cls, calendar):
    """The structured list representation remains supported."""
    assert cls.from_jcal(calendar.to_jcal()).to_ical() == calendar.to_ical()


@pytest.mark.parametrize("cls", PARSER_CLASSES)
def test_native_xcal_element(cls, calendar):
    """The structured XML representation remains supported."""
    assert (
        cls.from_xcal(config.parse_xml(BytesIO(calendar.to_xcal())).getroot())[0]
        == calendar
    )


@pytest.mark.parametrize(
    ("format_name", "encoding"),
    [
        ("jcal", "utf-16"),
        ("jcal", "utf-32"),
        ("xcal", "utf-16"),
        ("xcal", "iso-8859-1"),
    ],
)
@pytest.mark.parametrize("kind", ["bytes", "Path", "binary"])
def test_encoded_bytes(format_name, encoding, kind, calendar, tmp_path):
    """Byte inputs retain JSON/XML encoding detection rather than assuming UTF-8."""
    text = serialized(calendar, format_name).decode()
    if format_name == "xcal":
        if encoding == "iso-8859-1":
            text = text.replace("☕", "tea")
        text = text.split("?>", 1)[-1]
        text = f'<?xml version="1.0" encoding="{encoding}"?>' + text
    source = input_data(text.encode(encoding), kind, tmp_path)

    result = parse(Calendar, format_name, source)

    assert result.events[0].summary == (
        "Café tea" if encoding == "iso-8859-1" else "Café ☕"
    )


@pytest.mark.parametrize("encoding", ["utf-16", "iso-8859-1"])
@pytest.mark.parametrize("kind", ["str", "StringIO", "file", "temporary", "codecs"])
def test_decoded_xml_declaration(encoding, kind, calendar, tmp_path):
    """Decoded XML is not reinterpreted using its original byte encoding."""
    text = calendar.to_xcal().decode().split("?>", 1)[-1]
    if encoding == "iso-8859-1":
        text = text.replace("☕", "tea")
    text = f'<?xml version="1.0" encoding="{encoding}"?>' + text
    expected = "Café tea" if encoding == "iso-8859-1" else "Café ☕"

    def check(source):
        assert Calendar.from_xcal(source)[0].events[0].summary == expected
        if kind != "str":
            assert not source.closed

    if kind == "str":
        check(text)
    elif kind == "StringIO":
        source = StringIO(STREAM_PREFIX + text)
        source.read(len(STREAM_PREFIX))
        check(source)
    elif kind == "temporary":
        with NamedTemporaryFile(mode="w+", encoding=encoding, dir=tmp_path) as source:
            source.write(STREAM_PREFIX + text)
            source.seek(0)
            source.read(len(STREAM_PREFIX))
            check(source)
    else:
        path = tmp_path / "calendar.xml"
        path.write_text(STREAM_PREFIX + text, encoding=encoding)
        with (
            codecs.open(path, encoding=encoding)
            if kind == "codecs"
            else path.open(encoding=encoding)
        ) as source:
            source.read(len(STREAM_PREFIX))
            check(source)


@pytest.mark.parametrize("format_name", FORMATS)
@pytest.mark.parametrize("kind", STREAM_KINDS)
def test_caller_stream_remains_open_after_error(format_name, kind, tmp_path):
    """Invalid data does not transfer ownership of the caller's open file."""
    source = input_data(b"invalid data", kind, tmp_path)

    with pytest.raises((ValueError, ParseError)):
        parse(Calendar, format_name, source)

    assert not source.closed


@pytest.mark.parametrize("format_name", FORMATS)
@pytest.mark.parametrize("valid", [True, False])
def test_path_file_is_closed(format_name, valid, calendar, tmp_path, monkeypatch):
    """Files opened by a parser are closed on successful and failed parsing."""
    path = tmp_path / "calendar.data"
    path.write_bytes(serialized(calendar, format_name) if valid else b"invalid data")
    opened = []
    original_open = Path.open

    def tracking_open(self, *args, **kwargs):
        file = original_open(self, *args, **kwargs)
        opened.append(file)
        return file

    monkeypatch.setattr(Path, "open", tracking_open)
    if valid:
        assert parse(Calendar, format_name, path) == calendar
    else:
        with pytest.raises((ValueError, ParseError)):
            parse(Calendar, format_name, path)

    assert len(opened) == 1
    assert opened[0].closed


@pytest.mark.parametrize("format_name", FORMATS)
def test_string_is_data_not_a_filename(format_name, calendar, tmp_path):
    """Existing file names passed as strings are never implicitly opened."""
    path = tmp_path / "calendar.data"
    path.write_bytes(serialized(calendar, format_name))

    with pytest.raises((ValueError, ParseError)):
        parse(Calendar, format_name, str(path))


@pytest.mark.parametrize("cls", PARSER_CLASSES)
@pytest.mark.parametrize("kind", STREAM_KINDS)
def test_multiple_ical_components(cls, kind, calendar, tmp_path):
    """File inputs retain the multiple-component parsing option."""
    source = input_data(calendar.to_ical() * 2, kind, tmp_path)

    assert cls.from_ical(source, multiple=True) == [calendar, calendar]
    assert not source.closed


@pytest.mark.parametrize("format_name", FORMATS)
def test_custom_factory(format_name, calendar):
    """Normalizing serialized inputs still uses the entry class's factory."""

    class CustomEvent(Event):
        pass

    class CustomCalendar(Calendar):
        _components_factory = ComponentFactory()

    CustomCalendar._components_factory.add_component_class(CustomEvent)
    source = BytesIO(serialized(calendar, format_name))

    assert isinstance(parse(CustomCalendar, format_name, source).events[0], CustomEvent)


@pytest.mark.parametrize("kind", STREAM_KINDS)
def test_configured_xml_parser_receives_caller_stream(
    kind, calendar, tmp_path, monkeypatch
):
    """The configurable XML parser retains the original stream and its position."""
    source = input_data(calendar.to_xcal(), kind, tmp_path)
    original_parse = config.parse_xml
    seen = []

    def parse_xml(file):
        seen.append(file)
        assert file is source
        assert file.tell() == len(STREAM_PREFIX)
        return original_parse(file)

    monkeypatch.setattr(config, "parse_xml", parse_xml)

    assert Calendar.from_xcal(source) == [calendar]
    assert seen == [source]
    assert not source.closed
