r"""Regression tests for issue #1445.

:rfc:`7265` reserves the ``unknown`` value type for properties whose value type
is not known (unrecognized properties, ``X-`` properties without a ``VALUE``
parameter, ``IMAGE``). Such values MUST be carried into and out of iCalendar
*without processing* -- no :rfc:`5545` escaping or unescaping -- so they
round-trip byte-for-byte (:rfc:`7265#section-5.1` / :rfc:`7265#section-5.2`).

These tests pin down, in every direction:

* unknown values are preserved verbatim;
* known types (including ``VALUE=TEXT``) still get TEXT escaping (R1 boundary);
* unrecognized *parameters* are still treated as TEXT, not verbatim (R2);
* :class:`~icalendar.prop.unknown.vUnknown` no longer inherits from
  :class:`~icalendar.prop.text.vText`, but shares its plumbing.
"""

import pytest

from icalendar.cal import Component
from icalendar.prop import vDDDTypes, vText, vUnknown


def _event(line: str) -> Component:
    """Parse a one-property VEVENT from a raw content ``line``."""
    ics = f"BEGIN:VEVENT\r\nUID:1\r\n{line}\r\nEND:VEVENT\r\n"
    return Component.from_ical(ics)


def _line(component: Component, name: str) -> str:
    """Return the serialized content line for ``name`` (unfolded, single line)."""
    for serialized in component.to_ical().decode().split("\r\n"):
        if serialized.startswith(name):
            return serialized
    raise AssertionError(f"{name} not serialized in {component.to_ical()!r}")


# Value text exactly as it appears in the content line after the colon. Each is
# an unknown value (X-MYSTERY) that must survive untouched. Mix of bare and
# escaped specials, both newline spellings, and a date-time-looking value.
VERBATIM_VALUES = [
    r"Stenophylla;Guinea\,Africa",  # RFC 7265 section 5.3 coffee example
    r"a;b",  # bare semicolon
    r"a,b",  # bare comma
    r"a\,b",  # escaped comma
    r"a\;b",  # escaped semicolon
    r"a\\b",  # escaped backslash
    r"a\:b",  # escaped colon (not even legal TEXT)
    r"a\nb",  # literal backslash-n (must NOT become a real newline)
    r"a\Nb",  # literal backslash-N
    "20110512T120000Z",  # default type would be unknown
]


@pytest.mark.parametrize("raw", VERBATIM_VALUES)
def test_unknown_value_is_verbatim_in_every_direction(raw):
    """An unknown value is preserved byte-for-byte through every conversion."""
    ev = _event(f"X-MYSTERY:{raw}")
    prop = ev["X-MYSTERY"]

    # the resolved type is the reserved unknown type
    assert isinstance(prop, vUnknown)
    # reading the value gives the unprocessed text (no unescaping)
    assert str(prop) == raw

    # iCal -> iCal
    assert _line(ev, "X-MYSTERY") == f"X-MYSTERY:{raw}"
    # iCal -> jCal: value is the raw text, type is "unknown"
    assert ev.to_jcal()[1][1] == ["x-mystery", {}, "unknown", raw]
    # jCal -> iCal
    assert _line(Component.from_jcal(ev.to_jcal()), "X-MYSTERY") == f"X-MYSTERY:{raw}"


@pytest.mark.parametrize("raw", VERBATIM_VALUES)
def test_unknown_value_round_trips_are_stable(raw):
    """iCal -> jCal -> iCal and jCal -> iCal -> jCal are fixpoints."""
    ev = _event(f"X-MYSTERY:{raw}")

    ical_jcal_ical = Component.from_jcal(ev.to_jcal()).to_ical()
    assert ical_jcal_ical == ev.to_ical()

    jcal = ev.to_jcal()
    jcal_ical_jcal = Component.from_jcal(jcal).to_jcal()
    assert jcal_ical_jcal == jcal


@pytest.mark.parametrize(
    ("ical", "jcal_value"),
    [
        ("X-COMPLAINT-DEADLINE:20110512T120000Z", "20110512T120000Z"),
        (r"X-COFFEE-DATA:Stenophylla;Guinea\,Africa", r"Stenophylla;Guinea\,Africa"),
    ],
)
def test_rfc_7265_section_5_3_examples(ical, jcal_value):
    """The two literal examples from RFC 7265 section 5.3."""
    name = ical.split(":")[0]
    ev = _event(ical)
    assert ev.to_jcal()[1][1] == [name.lower(), {}, "unknown", jcal_value]
    assert _line(ev, name) == ical


def test_read_only_access_returns_unprocessed_text():
    """Reading an unknown value yields the verbatim text, not a decoded form."""
    ev = _event(r"X-COFFEE-DATA:Stenophylla;Guinea\,Africa")
    assert str(ev["X-COFFEE-DATA"]) == r"Stenophylla;Guinea\,Africa"
    # decoded() returns the unprocessed text (verbatim), like a parsed vText
    assert ev.decoded("X-COFFEE-DATA") == r"Stenophylla;Guinea\,Africa"


# --- R1 boundary: an explicit VALUE declares the type, so it is NOT unknown ---


def test_value_text_still_escapes():
    """VALUE=TEXT means the author declared TEXT: normal escaping applies."""
    ev = _event(r"X-FOO;VALUE=TEXT:a;b\,c")
    assert isinstance(ev["X-FOO"], vText)
    assert not isinstance(ev["X-FOO"], vUnknown)
    # the bare ';' gets escaped, like any TEXT value
    assert _line(ev, "X-FOO") == r"X-FOO;VALUE=TEXT:a\;b\,c"
    assert ev.to_jcal()[1][1][2] == "text"


def test_value_recognized_type_is_parsed():
    """A recognized VALUE type is parsed as that type, not treated as unknown."""
    ev = _event("X-WHEN;VALUE=DATE:20110512")
    assert isinstance(ev["X-WHEN"], vDDDTypes)
    assert ev.to_jcal()[1][1] == ["x-when", {}, "date", "2011-05-12"]


def test_value_unrecognized_type_round_trips_losslessly():
    """An unrecognized VALUE type keeps its name and a verbatim value.

    The jCal type field is the custom name (not ``unknown``), so the VALUE
    parameter survives the round-trip rather than being dropped.
    """
    ev = _event(r"X-FOO;VALUE=FOOBAR:x;y\,z")
    assert isinstance(ev["X-FOO"], vUnknown)
    assert ev.to_jcal()[1][1] == ["x-foo", {}, "foobar", r"x;y\,z"]

    back = Component.from_jcal(ev.to_jcal())
    assert _line(back, "X-FOO") == r"X-FOO;VALUE=FOOBAR:x;y\,z"


# --- R2: unrecognized PARAMETERS are still treated as TEXT, not verbatim ---


def test_unrecognized_parameter_is_decoded_not_verbatim():
    """Parameters are decoded (RFC 7265 section 5.1), only the value is verbatim."""
    ev = _event('X-FOO;X-ROAST="a,b;c";X-NOTE=line1^nline2:val;ue')
    prop = ev["X-FOO"]

    # value: verbatim, no decoding (bare ';' kept)
    assert str(prop) == "val;ue"

    # parameters: decoded, not verbatim
    assert prop.params["X-ROAST"] == "a,b;c"  # de-quoted
    assert prop.params["X-NOTE"] == "line1\nline2"  # RFC 6868 ^n -> newline

    assert ev.to_jcal()[1][1] == [
        "x-foo",
        {"x-roast": "a,b;c", "x-note": "line1\nline2"},
        "unknown",
        "val;ue",
    ]


@pytest.mark.parametrize(
    ("line", "jcal_type"),
    [
        ("IMAGE", "unknown"),  # no VALUE parameter
        ("IMAGE;VALUE=URI", "uri"),  # an explicit VALUE does not change the handling
        ("IMAGE;VALUE=BINARY", "binary"),
    ],
)
def test_image_value_is_verbatim(line, jcal_type):
    """IMAGE always resolves to the unknown type and is preserved verbatim.

    This is not a consequence of IMAGE lacking a VALUE parameter. IMAGE is
    special-cased in ``TypesFactory.for_property`` to always resolve to the
    unknown type, even when VALUE is URI or BINARY, so that image data is not
    corrupted by escaping (see commit aac97fa9). An explicit VALUE is still
    preserved as the jCal type field, but the value stays verbatim either way.

    Note: whether IMAGE should honor VALUE (vUri/vBinary) instead of always
    resolving to unknown is tracked separately in issue #1561. This test pins
    the current behavior; it will need updating if that changes.
    """
    ev = _event(rf"{line}:a;b\,c")
    assert isinstance(ev["IMAGE"], vUnknown)
    assert _line(ev, "IMAGE") == rf"{line}:a;b\,c"
    assert ev.to_jcal()[1][1] == ["image", {}, jcal_type, r"a;b\,c"]


def test_known_text_property_is_unaffected():
    """A known TEXT property still escapes and round-trips exactly as before."""
    ev = _event(r"SUMMARY:a\;b\,c")
    assert isinstance(ev["SUMMARY"], vText)
    assert str(ev["SUMMARY"]) == "a;b,c"  # TEXT is unescaped on read
    assert _line(ev, "SUMMARY") == r"SUMMARY:a\;b\,c"


def test_jcal_unknown_value_with_raw_newline_fails_safely():
    """A jCal unknown value with a raw newline cannot be a bare iCal value.

    This is only reachable from jCal (an iCal content line cannot carry a raw
    newline). It fails loudly rather than emitting invalid iCalendar.
    """
    jcal = ["vevent", [["uid", {}, "text", "1"], ["x-m", {}, "unknown", "a\nb"]], []]
    with pytest.raises((AssertionError, ValueError)):
        Component.from_jcal(jcal).to_ical()


# --- vUnknown / vText relationship ---


def test_vunknown_does_not_inherit_vtext():
    """The classes are deliberately independent (issue #1445 / RFC 7265)."""
    assert not issubclass(vUnknown, vText)
    assert vText.__name__ not in [c.__name__ for c in vUnknown.__mro__]


@pytest.mark.parametrize("cls", [vText, vUnknown])
def test_shared_string_plumbing(cls):
    """vText and vUnknown share construction/jCal plumbing (the duplication must not drift)."""
    obj = cls("hello", params={"X-P": "v"})
    assert str(obj) == "hello"
    assert obj.ical_value == "hello"
    assert obj.params["X-P"] == "v"
    assert isinstance(cls.from_ical("z"), cls)
    name, params, _vtype, value = obj.to_jcal("x-foo")
    assert (name, params, value) == ("x-foo", {"x-p": "v"}, "hello")


def test_diverging_to_ical_behavior():
    """The one place the two classes differ: escaping vs verbatim."""
    assert vText("a;b").to_ical() == rb"a\;b"
    assert vUnknown("a;b").to_ical() == b"a;b"


def test_diverging_jcal_type_field():
    """vText serializes as ``text``; vUnknown as ``unknown``."""
    assert vText("x").to_jcal("x-foo")[2] == "text"
    assert vUnknown("x").to_jcal("x-foo")[2] == "unknown"
