"""Conferences according to Section 5.11 of :rfc:`7986`."""

from __future__ import annotations

from dataclasses import dataclass

from icalendar.prop import vUri


@dataclass
class Conference:
    """Conferences according to Section 5.11 of :rfc:`7986`.

    Purpose:
        Information for accessing a conferencing system.

    Conformance:
        This property can be specified multiple times in a
        "VEVENT" or "VTODO" calendar component.

    Description:
        This property specifies information for accessing a
        conferencing system for attendees of a meeting or task.  This
        might be for a telephone-based conference number dial-in with
        access codes included (such as a tel: URI :rfc:`3966` or a sip: or
        sips: URI :rfc:`3261`), for a web-based video chat (such as an http:
        or https: URI :rfc:`7230`), or for an instant messaging group chat
        room (such as an xmpp: URI :rfc:`5122`).  If a specific URI for a
        conferencing system is not available, a data: URI :rfc:`2397`
        containing a text description can be used.

        A conference system can be a bidirectional communication channel
        or a uni-directional "broadcast feed".

        The "FEATURE" property parameter is used to describe the key
        capabilities of the conference system to allow a client to choose
        the ones that give the required level of interaction from a set of
        multiple properties.

        The "LABEL" property parameter is used to convey additional
        details on the use of the URI.  For example, the URIs or access
        codes for the moderator and attendee of a teleconference system
        could be different, and the "LABEL" property parameter could be
        used to "tag" each "CONFERENCE" property to indicate which is
        which.

        The "LANGUAGE" property parameter can be used to specify the
        language used for text values used with this property (as per
        Section 3.2.10 of :rfc:`5545`).

    Example:
        The following are examples of this property:

        .. code-block:: text

            CONFERENCE;VALUE=URI;FEATURE=PHONE,MODERATOR;
             LABEL=Moderator dial-in:tel:+1-412-555-0123,,,654321
            CONFERENCE;VALUE=URI;FEATURE=PHONE;
             LABEL=Attendee dial-in:tel:+1-412-555-0123,,,555123
            CONFERENCE;VALUE=URI;FEATURE=PHONE;
             LABEL=Attendee dial-in:tel:+1-888-555-0456,,,555123
            CONFERENCE;VALUE=URI;FEATURE=CHAT;
             LABEL=Chat room:xmpp:chat-123@conference.example.com
            CONFERENCE;VALUE=URI;FEATURE=AUDIO,VIDEO;
             LABEL=Attendee dial-in:https://chat.example.com/audio?id=123456
    """

    # see https://stackoverflow.com/a/18348004/1320237
    uri: str
    feature: list[str] | str | None = None
    label: list[str] | str | None = None
    language: list[str] | str | None = None

    @classmethod
    def from_uri(cls, uri: vUri | str):
        """Create a Conference from a URI."""
        if isinstance(uri, str) and not isinstance(uri, vUri):
            uri = vUri(uri)
        return cls(
            uri,
            feature=uri.params.get("feature"),
            label=uri.params.get("label"),
            language=uri.params.get("language"),
        )

    def to_uri(self) -> vUri:
        """Convert the Conference to a vUri."""
        params = {}
        if self.feature:
            params["FEATURE"] = self.feature
        if self.label:
            params["LABEL"] = self.label
        if self.language:
            params["LANGUAGE"] = self.language
        return vUri(self.uri, params=params)


__all__ = ["Conference"]
