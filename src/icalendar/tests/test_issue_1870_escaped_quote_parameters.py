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
"""

from icalendar import Calendar, Event
from icalendar.parser import Contentline, Parameters, q_split
from icalendar.parser.parameter import unescape_quoted_param_value

BS = "\\"
Q = '"'


def _event_with(line: str) -> Event:
    return Event.from_ical(
        f"BEGIN:VEVENT\r\n{line}\r\nSUMMARY:still here\r\nEND:VEVENT\r\n"
    )


class TestUnescapeQuotedParamValue:
    def test_escaped_quote_becomes_literal_quote(self) -> None:
        assert unescape_quoted_param_value(f"Qu{BS}{Q}ote") == f"Qu{Q}ote"

    def test_escaped_backslash_becomes_literal_backslash(self) -> None:
        assert unescape_quoted_param_value(f"a{BS}{BS}b") == f"a{BS}b"

    def test_left_to_right_scan_for_backslash_backslash_quote(self) -> None:
        # \\\" is an escaped backslash followed by an escaped quote -> \"
        assert unescape_quoted_param_value(f"a{BS}{BS}{BS}{Q}b") == f"a{BS}{Q}b"

    def test_lone_backslash_is_kept(self) -> None:
        assert unescape_quoted_param_value(f"a{BS}xb") == f"a{BS}xb"

    def test_trailing_lone_backslash_is_kept(self) -> None:
        assert unescape_quoted_param_value(f"abc{BS}") == f"abc{BS}"

    def test_plain_value_is_unchanged(self) -> None:
        assert unescape_quoted_param_value("Doe, John") == "Doe, John"

    def test_multiple_escaped_quotes(self) -> None:
        assert unescape_quoted_param_value(f"{Q}a{Q}{BS}{Q} and {BS}{Q}b{Q}") == (
            f"{Q}a{Q}{Q} and {Q}b{Q}"
        )

    def test_empty_value_is_unchanged(self) -> None:
        assert unescape_quoted_param_value("") == ""


class TestQSplit:
    def test_comma_inside_escaped_quotes_does_not_split(self) -> None:
        assert q_split(f'CN="Qu{BS}"ote, Jr"') == [f'CN="Qu{BS}"ote, Jr"']

    def test_plain_quoted_comma_does_not_split(self) -> None:
        assert q_split('"a,b"') == ['"a,b"']

    def test_unquoted_comma_splits(self) -> None:
        assert q_split("a,b") == ["a", "b"]

    def test_docstring_examples_unchanged(self) -> None:
        assert q_split("a,b,c") == ["a", "b", "c"]
        assert q_split('a,"b,c",d') == ["a", '"b,c"', "d"]
        assert q_split("a;b;c", sep=";") == ["a", "b", "c"]

    def test_semicolon_inside_escaped_quotes_does_not_split(self) -> None:
        assert q_split(f'ALTREP="http://x{BS}"y";other', sep=";") == [
            f'ALTREP="http://x{BS}"y"',
            "other",
        ]

    def test_escaped_quote_then_separator_splits_after_closing_quote(self) -> None:
        assert q_split(f'"a{BS}"b",c') == [f'"a{BS}"b"', "c"]

    def test_maxsplit_is_respected(self) -> None:
        assert q_split("a,b,c", maxsplit=1) == ["a", "b,c"]


class TestContentline:
    LINE = f'ATTENDEE;CN="Qu{BS}{Q}ote":mailto:x@y.z'

    def test_value_separator_is_found(self) -> None:
        assert Contentline(self.LINE).value_separator_index() == len(
            f'ATTENDEE;CN="Qu{BS}{Q}ote"'
        )

    def test_value_separator_with_plain_quoted_colon(self) -> None:
        line = 'DESCRIPTION;ALTREP="http://x:y/z":plain'
        assert Contentline(line).value_separator_index() == len(
            'DESCRIPTION;ALTREP="http://x:y/z"'
        )

    def test_raw_parts_split_correctly(self) -> None:
        name, params, value = Contentline(self.LINE).raw_parts()
        assert name == "ATTENDEE"
        assert value == "mailto:x@y.z"
        assert params["CN"] == f"Qu{Q}ote"

    def test_parts_split_correctly(self) -> None:
        name, params, value = Contentline(self.LINE).parts()
        assert name == "ATTENDEE"
        assert value == "mailto:x@y.z"
        assert params["CN"] == f"Qu{Q}ote"

    def test_multiple_parameters_around_an_escaped_quote(self) -> None:
        line = f'ATTENDEE;RSVP=TRUE;CN="Qu{BS}{Q}ote";ROLE=REQ-PARTICIPANT:mailto:x@y.z'
        name, params, value = Contentline(line).parts()
        assert name == "ATTENDEE"
        assert value == "mailto:x@y.z"
        assert params["RSVP"] == "TRUE"
        assert params["ROLE"] == "REQ-PARTICIPANT"
        assert params["CN"] == f"Qu{Q}ote"

    def test_raw_unescaped_quote_in_quoted_value_still_rejected(self) -> None:
        # a "quote" that is not escaped is not valid inside a quoted value
        line = 'ATTENDEE;CN="Qu"ote":mailto:x@y.z'
        try:
            Contentline(line).parts()
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for an unescaped quote")


class TestParametersFromIcal:
    def test_cn_with_escaped_quote(self) -> None:
        params = Parameters.from_ical(f'CN="Qu{BS}{Q}ote"')
        assert params["CN"] == f"Qu{Q}ote"

    def test_cn_with_comma_still_works(self) -> None:
        assert Parameters.from_ical('CN="Doe, John"')["CN"] == "Doe, John"

    def test_unquoted_value_still_works(self) -> None:
        assert Parameters.from_ical("RSVP=TRUE")["RSVP"] == "TRUE"

    def test_comma_list_with_escaped_quote_member(self) -> None:
        params = Parameters.from_ical(f'MEMBER="a{BS}{Q}b",c')
        assert params["MEMBER"] == [f"a{Q}b", "c"]

    def test_escaped_backslash_in_quoted_value(self) -> None:
        params = Parameters.from_ical(f'X-PATH="C:{BS}{BS}folder"')
        assert params["X-PATH"] == f"C:{BS}folder"

    def test_smith_john_real_world_shape(self) -> None:
        params = Parameters.from_ical(f'CN="Smith, {BS}{Q}John{BS}{Q}"')
        assert params["CN"] == f"Smith, {Q}John{Q}"


class TestEventParsing:
    LINE = f'ATTENDEE;CN="Qu{BS}{Q}ote":mailto:x@y.z'

    def test_issue_repro_property_survives(self) -> None:
        event = _event_with(self.LINE)
        assert event.get("ATTENDEE") is not None

    def test_issue_repro_cn_value(self) -> None:
        event = _event_with(self.LINE)
        assert event["ATTENDEE"].params["CN"] == f"Qu{Q}ote"

    def test_issue_repro_value_and_neighbors(self) -> None:
        event = _event_with(self.LINE)
        assert event["ATTENDEE"] == "mailto:x@y.z"
        assert event["SUMMARY"] == "still here"

    def test_organizer_with_escaped_quote(self) -> None:
        event = _event_with(f'ORGANIZER;CN="Bo{BS}{Q}ss":mailto:b@oss.de')
        assert event["ORGANIZER"].params["CN"] == f"Bo{Q}ss"

    def test_multiple_attendees_one_with_escaped_quote(self) -> None:
        event = _event_with(
            f'ATTENDEE;CN=Plain:mailto:a@b.c\r\nATTENDEE;CN="Ex{BS}{Q}tra":mailto:c@d.e'
        )
        attendees = event.get("ATTENDEE")
        assert list(attendees)[0].params["CN"] == "Plain"
        assert list(attendees)[1].params["CN"] == f"Ex{Q}tra"

    def test_strict_contentline_is_lenient_too(self) -> None:
        _name, params, _value = Contentline(self.LINE, strict=True).parts()
        assert params["CN"] == f"Qu{Q}ote"

    def test_calendar_walk_keeps_the_property(self) -> None:
        ical = (
            "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//t//t//EN\r\n"
            "BEGIN:VEVENT\r\n"
            f"{self.LINE}\r\n"
            "END:VEVENT\r\nEND:VCALENDAR\r\n"
        )
        (event,) = Calendar.from_ical(ical).walk("VEVENT")
        assert event["ATTENDEE"].params["CN"] == f"Qu{Q}ote"

    def test_vtodo_also_keeps_the_property(self) -> None:
        from icalendar import Todo

        ical = (
            f'BEGIN:VTODO\r\nATTENDEE;CN="Qu{BS}{Q}ote":mailto:x@y.z\r\nEND:VTODO\r\n'
        )
        todo = Todo.from_ical(ical)
        assert todo["ATTENDEE"].params["CN"] == f"Qu{Q}ote"

    def test_escaped_quote_with_semicolon_and_colon_inside(self) -> None:
        event = _event_with(f'ATTENDEE;CN="a{BS}{Q}b;c:d":mailto:x@y.z')
        assert event["ATTENDEE"].params["CN"] == f"a{Q}b;c:d"

    def test_escaped_quote_altrep(self) -> None:
        event = _event_with(f'DESCRIPTION;ALTREP="http://x/{BS}{Q}y":plain')
        assert event["DESCRIPTION"].params["ALTREP"] == f"http://x/{Q}y"
        assert event["DESCRIPTION"] == "plain"

    def test_reserialization_keeps_the_participant(self) -> None:
        event = _event_with(self.LINE)
        out = event.to_ical()
        reparsed = Event.from_ical(out)
        # output replaces the quote with ' (param values may not carry "),
        # but the attendee and its CN must both still be there
        assert reparsed.get("ATTENDEE") is not None
        assert "CN" in reparsed["ATTENDEE"].params
