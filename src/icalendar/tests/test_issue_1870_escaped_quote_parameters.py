r"""Escaped double quotes inside quoted parameter values.

See https://github.com/collective/icalendar/issues/1870

A content line such as ``ATTENDEE;CN="Qu\\"ote":mailto:x@y.z`` used to be
dropped silently: the quote tracking toggled on every double quote, so the
``\\"`` inside the value looked like it closed the quoted section and the
value-separating colon appeared to be inside quotes. The whole property
disappeared from the parsed component.

``\\"`` inside a quoted parameter value is now treated as a literal double
quote (:rfc:`2445`-style escaping that real-world files still carry), the
line parses, and the parameter value keeps its quote.

Scope decisions (see the review discussion on PR #1871):

- **:rfc:`6868` (CARET encoding)** applies to *serializing* parameter
  values: icalendar already emits ``^'`` for a literal DQUOTE on output
  (see :func:`icalendar.parser.parameter.rfc_6868_escape`), and this
  module verifies that round-trip. Parsing backslash-escaped DQOUTEs from
  existing files — the fix this module tests — is complementary, not
  conflicting: read accepts both, write uses the current RFC.
- **Unquoted parameter values** cannot carry an escaped quote: a raw
  DQUOTE is not a SAFE-CHAR in unquoted values (:rfc:`5545` §3.1), so the
  validator rejects it before any unescaping happens. The case does not
  arise and is tested as rejected.
- **Escapes in the value part** (after the ``:``) belong to the TEXT
  unescaper, not the parameter unescaper; the content-line splitter
  leaves them alone and the tests verify the split.
"""

import pytest

from icalendar import Calendar, Event
from icalendar.parser import Contentline, Parameters, q_split
from icalendar.parser.parameter import unescape_quoted_param_value

BS = "\\"
Q = '"'

# ---------------------------------------------------------------------------
# Shared escape scenarios, parametrized across every parsing layer so the
# same input is verified consistently (see the maintainer's review of #1871).
# Each case: (raw-in-quoted-value, expected-unescaped)
# ---------------------------------------------------------------------------
ESCAPE_CASES = [
    pytest.param(f"Qu{BS}{Q}ote", f"Qu{Q}ote", id="single_escaped_quote"),
    pytest.param(f"a{BS}{BS}b", f"a{BS}b", id="escaped_backslash"),
    pytest.param(f"a{BS}{BS}{BS}{Q}b", f"a{BS}{Q}b", id="escaped_backslash_then_quote"),
    pytest.param(f"{BS}{Q}", f"{Q}", id="escaped_quote_alone"),
    pytest.param(f"{BS}{BS}", f"{BS}", id="escaped_backslash_alone"),
    pytest.param(f"x{BS}{Q}y{BS}{Q}z", f"x{Q}y{Q}z", id="two_escaped_quotes"),
    pytest.param(f"a{BS}xb", f"a{BS}xb", id="lone_backslash_kept"),
    pytest.param(f"abc{BS}", f"abc{BS}", id="trailing_backslash_kept"),
    pytest.param("Doe, John", "Doe, John", id="no_escapes"),
    pytest.param("", "", id="empty"),
]


# ---------------------------------------------------------------------------
# Layer 1: the unescape helper
# ---------------------------------------------------------------------------
class TestUnescapeQuotedParamValue:
    @pytest.mark.parametrize(("raw", "expected"), ESCAPE_CASES)
    def test_unescape(self, raw, expected):
        assert unescape_quoted_param_value(raw) == expected

    def test_multiple_escaped_quotes_intention(self):
        r"""Several escaped quotes in one value each become a literal DQUOTE.

        Producers that emit display names with quotation marks (e.g.
        CN="Smith, \\"John\\"") round-trip through this path.
        """
        raw = f"{Q}a{Q}{BS}{Q} and {BS}{Q}b{Q}"
        assert unescape_quoted_param_value(raw) == f"{Q}a{Q}{Q} and {Q}b{Q}"


# ---------------------------------------------------------------------------
# Layer 2: q_split — quote-aware splitting
# ---------------------------------------------------------------------------
class TestQSplit:
    def test_comma_inside_escaped_quotes_does_not_split(self):
        assert q_split(f'CN="Qu{BS}"ote, Jr"') == [f'CN="Qu{BS}"ote, Jr"']

    def test_plain_quoted_comma_does_not_split(self):
        assert q_split('"a,b"') == ['"a,b"']

    def test_unquoted_comma_splits(self):
        assert q_split("a,b") == ["a", "b"]

    def test_docstring_examples_unchanged(self):
        assert q_split("a,b,c") == ["a", "b", "c"]
        assert q_split('a,"b,c",d') == ["a", '"b,c"', "d"]
        assert q_split("a;b;c", sep=";") == ["a", "b", "c"]

    def test_semicolon_inside_escaped_quotes_does_not_split(self):
        assert q_split(f'ALTREP="http://x{BS}"y";other', sep=";") == [
            f'ALTREP="http://x{BS}"y"',
            "other",
        ]

    def test_escaped_quote_then_separator_splits_after_closing_quote(self):
        assert q_split(f'"a{BS}"b",c') == [f'"a{BS}"b"', "c"]

    def test_maxsplit_is_respected(self):
        assert q_split("a,b,c", maxsplit=1) == ["a", "b,c"]

    def test_two_escaped_quotes_comma_still_inside(self):
        """Two escaped quotes in the same quoted section keep it open."""
        assert q_split(f'"a{BS}"b{BS}"c,d"') == [f'"a{BS}"b{BS}"c,d"']


# ---------------------------------------------------------------------------
# Layer 3: Contentline — name/params/value splitting
# ---------------------------------------------------------------------------
class TestContentline:
    LINE = f'ATTENDEE;CN="Qu{BS}{Q}ote":mailto:x@y.z'

    def test_value_separator_is_found(self):
        assert Contentline(self.LINE).value_separator_index() == len(
            f'ATTENDEE;CN="Qu{BS}{Q}ote"'
        )

    def test_value_separator_with_plain_quoted_colon(self):
        line = 'DESCRIPTION;ALTREP="http://x:y/z":plain'
        assert Contentline(line).value_separator_index() == len(
            'DESCRIPTION;ALTREP="http://x:y/z"'
        )

    @pytest.mark.parametrize(
        ("quoted_value", "expected"),
        [
            (f"Qu{BS}{Q}ote", f"Qu{Q}ote"),
            (f"x{BS}{Q}y{BS}{Q}z", f"x{Q}y{Q}z"),
            (f"{BS}{BS}{BS}{Q}b", f"{BS}{Q}b"),
            (f"a{BS}{BS}b", f"a{BS}b"),
        ],
        ids=["one_escape", "two_escapes", "backslash_then_quote", "backslash"],
    )
    def test_parts_split_correctly(self, quoted_value, expected):
        """The same escape patterns tested in q_split also parse correctly
        when they appear in a full content line."""
        line = f'ATTENDEE;CN="{quoted_value}":mailto:x@y.z'
        name, params, value = Contentline(line).parts()
        assert name == "ATTENDEE"
        assert value == "mailto:x@y.z"
        assert params["CN"] == expected

    def test_raw_parts_split_correctly(self):
        name, params, value = Contentline(self.LINE).raw_parts()
        assert name == "ATTENDEE"
        assert value == "mailto:x@y.z"
        assert params["CN"] == f"Qu{Q}ote"

    def test_multiple_parameters_around_an_escaped_quote(self):
        line = f'ATTENDEE;RSVP=TRUE;CN="Qu{BS}{Q}ote";ROLE=REQ-PARTICIPANT:mailto:x@y.z'
        name, params, value = Contentline(line).parts()
        assert name == "ATTENDEE"
        assert value == "mailto:x@y.z"
        assert params["RSVP"] == "TRUE"
        assert params["ROLE"] == "REQ-PARTICIPANT"
        assert params["CN"] == f"Qu{Q}ote"

    def test_raw_unescaped_quote_in_quoted_value_still_rejected(self):
        # a "quote" that is not escaped is not valid inside a quoted value
        line = 'ATTENDEE;CN="Qu"ote":mailto:x@y.z'
        with pytest.raises(ValueError):
            Contentline(line).parts()

    def test_x_prop_with_escaped_quote_in_param(self):
        """An X- property (non-standard) with an escaped quote in a param
        value inside a component parses the same way."""
        line = f'X-PROP;X-PARAM="text{BS}{Q}:content":value'
        name, params, value = Contentline(line).parts()
        assert name == "X-PROP"
        assert value == "value"
        assert params["X-PARAM"] == f"text{Q}:content"

    def test_escaped_quote_in_the_value_is_untouched(self):
        """Escapes in the *value* part (after the colon) are handled by the
        TEXT unescaper, not the parameter unescaper — the content line
        splitter must not consume them."""
        line = f'DESCRIPTION;CN="Qu{BS}{Q}ote":text{BS}nnewline'
        _name, params, value = Contentline(line).parts()
        assert params["CN"] == f"Qu{Q}ote"
        # the TEXT unescaper already converted {BS}n to a real newline
        assert value == "text\nnewline"


# ---------------------------------------------------------------------------
# Layer 4: Parameters.from_ical
# ---------------------------------------------------------------------------
class TestParametersFromIcal:
    @pytest.mark.parametrize(
        ("quoted_value", "expected"),
        [
            (f"Qu{BS}{Q}ote", f"Qu{Q}ote"),
            (f"x{BS}{Q}y{BS}{Q}z", f"x{Q}y{Q}z"),
            (f"{BS}{BS}{BS}{Q}b", f"{BS}{Q}b"),
            (f"a{BS}{BS}b", f"a{BS}b"),
            (f"Smith, {BS}{Q}John{BS}{Q}", f"Smith, {Q}John{Q}"),
        ],
        ids=[
            "single",
            "double",
            "backslash_then_quote",
            "backslash",
            "real_world_name",
        ],
    )
    def test_unescape(self, quoted_value, expected):
        params = Parameters.from_ical(f'CN="{quoted_value}"')
        assert params["CN"] == expected

    def test_cn_with_comma_still_works(self):
        assert Parameters.from_ical('CN="Doe, John"')["CN"] == "Doe, John"

    def test_unquoted_value_still_works(self):
        assert Parameters.from_ical("RSVP=TRUE")["RSVP"] == "TRUE"

    def test_comma_list_with_escaped_quote_member(self):
        params = Parameters.from_ical(f'MEMBER="a{BS}{Q}b",c')
        assert params["MEMBER"] == [f"a{Q}b", "c"]

    def test_unquoted_value_with_backslash_is_rejected(self):
        """In an *unquoted* parameter value a raw DQUOTE is not allowed
        (RFC 5545 §3.1 SAFE-CHAR excludes it), so the case of an
        "unquoted value with an escaped quote" cannot arise — the
        validator rejects the raw quote before any unescaping happens."""
        with pytest.raises(ValueError, match="not a valid parameter"):
            Parameters.from_ical(f"URL=http://x/{BS}{Q}y")

    def test_multiple_params_each_with_escapes(self):
        """Several escapes on one line, across multiple parameters."""
        params = Parameters.from_ical(f'CN="a{BS}{Q}b";X-OTHER="c{BS}{BS}d"')
        assert params["CN"] == f"a{Q}b"
        assert params["X-OTHER"] == f"c{BS}d"


# ---------------------------------------------------------------------------
# Layer 5: end-to-end component parsing
# ---------------------------------------------------------------------------
def _event_with(line: str) -> Event:
    return Event.from_ical(
        f"BEGIN:VEVENT\r\n{line}\r\nSUMMARY:still here\r\nEND:VEVENT\r\n"
    )


class TestEventParsing:
    LINE = f'ATTENDEE;CN="Qu{BS}{Q}ote":mailto:x@y.z'

    def test_issue_repro_property_survives(self):
        event = _event_with(self.LINE)
        assert event.get("ATTENDEE") is not None

    def test_issue_repro_cn_value(self):
        event = _event_with(self.LINE)
        assert event["ATTENDEE"].params["CN"] == f"Qu{Q}ote"

    def test_issue_repro_value_and_neighbors(self):
        event = _event_with(self.LINE)
        assert event["ATTENDEE"] == "mailto:x@y.z"
        assert event["SUMMARY"] == "still here"

    def test_organizer_with_escaped_quote(self):
        event = _event_with(f'ORGANIZER;CN="Bo{BS}{Q}ss":mailto:b@oss.de')
        assert event["ORGANIZER"].params["CN"] == f"Bo{Q}ss"

    def test_multiple_attendees_one_with_escaped_quote(self):
        event = _event_with(
            f'ATTENDEE;CN=Plain:mailto:a@b.c\r\nATTENDEE;CN="Ex{BS}{Q}tra":mailto:c@d.e'
        )
        attendees = event.get("ATTENDEE")
        assert list(attendees)[0].params["CN"] == "Plain"
        assert list(attendees)[1].params["CN"] == f"Ex{Q}tra"

    def test_strict_contentline_is_lenient_too(self):
        _name, params, _value = Contentline(self.LINE, strict=True).parts()
        assert params["CN"] == f"Qu{Q}ote"

    def test_calendar_walk_keeps_the_property(self):
        ical = (
            "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//EN\r\n"
            "BEGIN:VEVENT\r\n"
            f"{self.LINE}\r\n"
            "END:VEVENT\r\nEND:VCALENDAR\r\n"
        )
        (event,) = Calendar.from_ical(ical).walk("VEVENT")
        assert event["ATTENDEE"].params["CN"] == f"Qu{Q}ote"

    def test_vtodo_also_keeps_the_property(self):
        from icalendar import Todo

        ical = (
            f'BEGIN:VTODO\r\nATTENDEE;CN="Qu{BS}{Q}ote":mailto:x@y.z\r\nEND:VTODO\r\n'
        )
        todo = Todo.from_ical(ical)
        assert todo["ATTENDEE"].params["CN"] == f"Qu{Q}ote"

    def test_escaped_quote_with_semicolon_and_colon_inside(self):
        event = _event_with(f'ATTENDEE;CN="a{BS}{Q}b;c:d":mailto:x@y.z')
        assert event["ATTENDEE"].params["CN"] == f"a{Q}b;c:d"

    def test_escaped_quote_altrep(self):
        event = _event_with(f'DESCRIPTION;ALTREP="http://x/{BS}{Q}y":plain')
        assert event["DESCRIPTION"].params["ALTREP"] == f"http://x/{Q}y"
        assert event["DESCRIPTION"] == "plain"

    def test_x_prop_inside_component(self):
        """The X-PARAM with escaped quote and colon from TestContentline
        also survives full component parsing."""
        event = _event_with(f'X-PROP;X-PARAM="text{BS}{Q}:content":value')
        assert event["X-PROP"].params["X-PARAM"] == f"text{Q}:content"
        assert event["X-PROP"] == "value"

    def test_reserialization_keeps_the_participant(self):
        """The round-trip preserves the CN value: icalendar serializes a
        DQUOTE in a parameter value as RFC 6868 CARET encoding (^'),
        which parses back to a literal DQUOTE."""
        event = _event_with(self.LINE)
        out = event.to_ical()
        reparsed = Event.from_ical(out)
        assert reparsed.get("ATTENDEE") is not None
        assert reparsed["ATTENDEE"].params["CN"] == f"Qu{Q}ote"


class TestUnbalancedEscapes:
    """Edge cases where an escaped DQUOTE inside a parameter value may or
    may not be followed by a properly balanced closing quote.

    These tests document what actually happens for each shape so future
    maintainers can make an informed decision if the behavior needs to
    change (see the review discussion on PR #1871).
    """

    @pytest.mark.parametrize(
        "content",
        [
            "content",
            f"quoted{Q}content",
            f"content_with{BS}{Q}",
            "a : in it but no quote before",
        ],
        ids=[
            "plain_after_escape",
            "raw_quote_after_escape",
            "escaped_quote_after_escape",
            "colon_no_quote",
        ],
    )
    def test_x_prop_with_escape_parameter_before_last_quote(self, content):
        r"""An escaped DQUOTE inside a parameter value followed by content
        that may or may not provide a balanced closing quote.

        Only an *escaped* DQUOTE (``{BS}{Q}``) in the trailing content
        balances the escape tracking and allows the line to parse — the
        scanner sees the pair and treats it as content inside the quoted
        section. A *raw* DQUOTE does not help: the escape-aware parameter
        validator still finds an unmasked quote and rejects the value.
        Without any quote at all, the parameter section runs to the end
        and the value separator is never found.
        """
        line = f'X-PROP;X-PARAM="text{BS}{Q}:{content}'
        if content == f"content_with{BS}{Q}":
            # the trailing escaped DQUOTE balances: the line parses and
            # the param value absorbs everything up to the end
            name, params, _value = Contentline(line).parts()
            assert name == "X-PROP"
            assert params["X-PARAM"] is not None
        else:
            # raw quotes do not balance the escape tracking, and without
            # any quote the section is unterminated — both are rejected
            with pytest.raises(ValueError):
                Contentline(line).parts()

    def test_double_backslash_then_quote_alone(self):
        """``{BS}{BS}{Q}`` on its own: the left-to-right scan treats the
        first ``{BS}{BS}`` as an escaped backslash (literal ``{BS}``),
        then ``{Q}`` is a bare DQUOTE with no preceding backslash.

        The unescaper returns ``{BS}{Q}`` — a literal backslash followed
        by a literal DQUOTE. This is the correct reading for RFC 2445
        backslash escapes: each ``{BS}`` pairs with the character after
        it; a DQUOTE not preceded by the *second* of a pair is literal
        content. Producers emitting ``{BS}{BS}{Q}`` inside a quoted
        parameter value intended a literal backslash then a literal
        quote.
        """
        raw = f"{BS}{BS}{Q}"
        assert unescape_quoted_param_value(raw) == f"{BS}{Q}"

    def test_double_backslash_quote_in_parameter(self):
        """The same ``{BS}{BS}{Q}`` sequence inside a full parameter."""
        params = Parameters.from_ical(f'CN="{BS}{BS}{Q}"')
        assert params["CN"] == f"{BS}{Q}"

    def test_double_backslash_quote_in_contentline(self):
        r"""The same ``{BS}{BS}{Q}`` sequence in a full content line is
        rejected: the scanner processes pairs left-to-right, so the first
        ``{BS}{BS}`` is consumed as an escaped backslash pair, leaving the
        ``{Q}`` as a bare DQUOTE that closes the quoted section early.

        The parameter section then runs past the intended end and the
        value separator is consumed as parameter content — the line is
        rejected as malformed. This differs from the unescape helper
        (which processes it as two literals) because the scanner sees the
        raw wire format while the helper sees the already-extracted
        parameter value. A producer that intends ``{BS}{Q}`` (literal
        backslash + literal quote) inside a parameter value should emit
        ``{BS}{BS}{BS}{Q}`` (escaped backslash + escaped quote), which
        parses correctly.
        """
        line = f'ATTENDEE;CN="a{BS}{BS}{Q}b":mailto:x@y.z'
        with pytest.raises(ValueError, match="not a valid parameter"):
            Contentline(line).parts()
