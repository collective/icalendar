3.2. Property Parameters
========================

A property can have attributes with which it is associated.  These
"property parameters" contain meta-information about the property or
the property value.  Property parameters are provided to specify such
information as the location of an alternate text representation for a
property value, the language of a text property value, the value type
of the property value, and other attributes.

Property parameter values that contain the COLON, SEMICOLON, or COMMA
character separators MUST be specified as quoted-string text values.
Property parameter values MUST NOT contain the DQUOTE character.  The
DQUOTE character is used as a delimiter for parameter values that
contain restricted characters or URI text.  For example::

    DESCRIPTION;ALTREP="cid:part1.0001@example.org":The Fall'98 Wild
      Wizards Conference - - Las Vegas\, NV\, USA

Property parameter values that are not in quoted-strings are case-
insensitive.

The general property parameters defined by this memo are defined by
the following notation::

    icalparameter = altrepparam       ; Alternate text representation
                  / cnparam           ; Common name
                  / cutypeparam       ; Calendar user type
                  / delfromparam      ; Delegator
                  / deltoparam        ; Delegatee
                  / dirparam          ; Directory entry
                  / encodingparam     ; Inline encoding
                  / fmttypeparam      ; Format type
                  / fbtypeparam       ; Free/busy time type
                  / languageparam     ; Language for text
                  / memberparam       ; Group or list membership
                  / partstatparam     ; Participation status
                  / rangeparam        ; Recurrence identifier range
                  / trigrelparam      ; Alarm trigger relationship
                  / reltypeparam      ; Relationship type
                  / roleparam         ; Participation role
                  / rsvpparam         ; RSVP expectation
                  / sentbyparam       ; Sent by
                  / tzidparam         ; Reference to time zone object
                  / valuetypeparam    ; Property value data type
                  / other-param

    other-param   = (iana-param / x-param)

    iana-param  = iana-token "=" param-value *("," param-value)
    ; Some other IANA-registered iCalendar parameter.

    x-param     = x-name "=" param-value *("," param-value)
    ; A non-standard, experimental parameter.

Applications MUST ignore x-param and iana-param values they don't
recognize.


3.2.1 Alternate Text Representation
-----------------------------------

**Parameter Name:**  ALTREP

**Purpose:**  To specify an alternate text representation for the
property value.

**Format Definition:**  This property parameter is defined by the
following notation::

    altrepparam = "ALTREP" "=" DQUOTE uri DQUOTE

**Description**:  This parameter specifies a URI that points to an
alternate representation for a textual property value.  A property
specifying this parameter MUST also include a value that reflects
the default representation of the text value.  The URI parameter
value MUST be specified in a quoted-string.

.. note::

    While there is no restriction imposed on the URI schemes
    allowed for this parameter, Content Identifier (CID) [RFC2392],
    HTTP [RFC2616], and HTTPS [RFC2818] are the URI schemes most
    commonly used by current implementations.

**Example:**

::

    DESCRIPTION;ALTREP="CID:part3.msg.970415T083000@example.com":
     Project XYZ Review Meeting will include the following agenda
      items: (a) Market Overview\, (b) Finances\, (c) Project Man
     agement

The "ALTREP" property parameter value might point to a "text/html"
content portion.

::

    Content-Type:text/html
    Content-Id:<part3.msg.970415T083000@example.com>

    <html>
      <head>
       <title></title>
      </head>
      <body>
        <p>
          <b>Project XYZ Review Meeting</b> will include
          the following agenda items:
          <ol>
            <li>Market Overview</li>
            <li>Finances</li>
            <li>Project Management</li>
          </ol>
        </p>
      </body>
    </html>


3.2.2. Common Name
------------------

**Parameter Name:**  CN

**Purpose:**  To specify the common name to be associated with the
calendar user specified by the property.

**Format Definition:**  This property parameter is defined by the
following notation::

    cnparam    = "CN" "=" param-value

**Description:**  This parameter can be specified on properties with a
CAL-ADDRESS value type.  The parameter specifies the common name
to be associated with the calendar user specified by the property.
The parameter value is text.  The parameter value can be used for
display text to be associated with the calendar address specified
by the property.

**Example:**

::
       ORGANIZER;CN="John Smith":mailto:jsmith@example.com


3.2.3. Calendar User Type
-------------------------

**Parameter Name:**  CUTYPE

**Purpose:**  To identify the type of calendar user specified by the
property.

**Format Definition:**  This property parameter is defined by the
following notation::

::

    cutypeparam        = "CUTYPE" "="
                       ("INDIVIDUAL"   ; An individual
                      / "GROUP"        ; A group of individuals
                      / "RESOURCE"     ; A physical resource
                      / "ROOM"         ; A room resource
                      / "UNKNOWN"      ; Otherwise not known
                      / x-name         ; Experimental type
                      / iana-token)    ; Other IANA-registered
                                       ; type
    ; Default is INDIVIDUAL

**Description:**  This parameter can be specified on properties with a
CAL-ADDRESS value type.  The parameter identifies the type of
calendar user specified by the property.  If not specified on a
property that allows this parameter, the default is INDIVIDUAL.
Applications MUST treat x-name and iana-token values they don't
recognize the same way as they would the UNKNOWN value.

**Example:**

::

    ATTENDEE;CUTYPE=GROUP:mailto:ietf-calsch@example.org


3.2.4. Delegators
-----------------

**Parameter Name:**  DELEGATED-FROM

**Purpose:**  To specify the calendar users that have delegated their
participation to the calendar user specified by the property.

**Format Definition:**  This property parameter is defined by the
following notation::

    delfromparam       = "DELEGATED-FROM" "=" DQUOTE cal-address
                          DQUOTE *("," DQUOTE cal-address DQUOTE)

**Description:**  This parameter can be specified on properties with a
CAL-ADDRESS value type.  This parameter specifies those calendar
users that have delegated their participation in a group-scheduled
event or to-do to the calendar user specified by the property.
The individual calendar address parameter values MUST each be
specified in a quoted-string.

**Example:**

::

       ATTENDEE;DELEGATED-FROM="mailto:jsmith@example.com":mailto:
        jdoe@example.com

3.2.5. Delegatees
-----------------

   Parameter Name:  DELEGATED-TO

   Purpose:  To specify the calendar users to whom the calendar user
      specified by the property has delegated participation.

   Format Definition:  This property parameter is defined by the
      following notation:

       deltoparam = "DELEGATED-TO" "=" DQUOTE cal-address DQUOTE
                    *("," DQUOTE cal-address DQUOTE)

   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  This parameter specifies those calendar
      users whom have been delegated participation in a group-scheduled
      event or to-do by the calendar user specified by the property.
      The individual calendar address parameter values MUST each be
      specified in a quoted-string.







Desruisseaux                Standards Track                    [Page 17]

RFC 5545                       iCalendar                  September 2009


   Example:

       ATTENDEE;DELEGATED-TO="mailto:jdoe@example.com","mailto:jqpublic
        @example.com":mailto:jsmith@example.com

3.2.6.  Directory Entry Reference

   Parameter Name:  DIR

   Purpose:  To specify reference to a directory entry associated with
      the calendar user specified by the property.

   Format Definition:  This property parameter is defined by the
      following notation:

       dirparam   = "DIR" "=" DQUOTE uri DQUOTE

   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  The parameter specifies a reference to
      the directory entry associated with the calendar user specified by
      the property.  The parameter value is a URI.  The URI parameter
      value MUST be specified in a quoted-string.

         Note: While there is no restriction imposed on the URI schemes
         allowed for this parameter, CID [RFC2392], DATA [RFC2397], FILE
         [RFC1738], FTP [RFC1738], HTTP [RFC2616], HTTPS [RFC2818], LDAP
         [RFC4516], and MID [RFC2392] are the URI schemes most commonly
         used by current implementations.

   Example:

       ORGANIZER;DIR="ldap://example.com:6666/o=ABC%20Industries,
        c=US???(cn=Jim%20Dolittle)":mailto:jimdo@example.com

3.2.7.  Inline Encoding

   Parameter Name:  ENCODING

   Purpose:  To specify an alternate inline encoding for the property
      value.

   Format Definition:  This property parameter is defined by the
      following notation:








Desruisseaux                Standards Track                    [Page 18]

RFC 5545                       iCalendar                  September 2009


       encodingparam      = "ENCODING" "="
                          ( "8BIT"
          ; "8bit" text encoding is defined in [RFC2045]
                          / "BASE64"
          ; "BASE64" binary encoding format is defined in [RFC4648]
                          )

   Description:  This property parameter identifies the inline encoding
      used in a property value.  The default encoding is "8BIT",
      corresponding to a property value consisting of text.  The
      "BASE64" encoding type corresponds to a property value encoded
      using the "BASE64" encoding defined in [RFC2045].

      If the value type parameter is ";VALUE=BINARY", then the inline
      encoding parameter MUST be specified with the value
      ";ENCODING=BASE64".

   Example:

     ATTACH;FMTTYPE=text/plain;ENCODING=BASE64;VALUE=BINARY:TG9yZW
      0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIGFkaXBpc2ljaW
      5nIGVsaXQsIHNlZCBkbyBlaXVzbW9kIHRlbXBvciBpbmNpZGlkdW50IHV0IG
      xhYm9yZSBldCBkb2xvcmUgbWFnbmEgYWxpcXVhLiBVdCBlbmltIGFkIG1pbm
      ltIHZlbmlhbSwgcXVpcyBub3N0cnVkIGV4ZXJjaXRhdGlvbiB1bGxhbWNvIG
      xhYm9yaXMgbmlzaSB1dCBhbGlxdWlwIGV4IGVhIGNvbW1vZG8gY29uc2VxdW
      F0LiBEdWlzIGF1dGUgaXJ1cmUgZG9sb3IgaW4gcmVwcmVoZW5kZXJpdCBpbi
      B2b2x1cHRhdGUgdmVsaXQgZXNzZSBjaWxsdW0gZG9sb3JlIGV1IGZ1Z2lhdC
      BudWxsYSBwYXJpYXR1ci4gRXhjZXB0ZXVyIHNpbnQgb2NjYWVjYXQgY3VwaW
      RhdGF0IG5vbiBwcm9pZGVudCwgc3VudCBpbiBjdWxwYSBxdWkgb2ZmaWNpYS
      BkZXNlcnVudCBtb2xsaXQgYW5pbSBpZCBlc3QgbGFib3J1bS4=

3.2.8.  Format Type

   Parameter Name:  FMTTYPE

   Purpose:  To specify the content type of a referenced object.

   Format Definition:  This property parameter is defined by the
      following notation:

       fmttypeparam = "FMTTYPE" "=" type-name "/" subtype-name
                      ; Where "type-name" and "subtype-name" are
                      ; defined in Section 4.2 of [RFC4288].

   Description:  This parameter can be specified on properties that are
      used to reference an object.  The parameter specifies the media
      type [RFC4288] of the referenced object.  For example, on the
      "ATTACH" property, an FTP type URI value does not, by itself,



Desruisseaux                Standards Track                    [Page 19]

RFC 5545                       iCalendar                  September 2009


      necessarily convey the type of content associated with the
      resource.  The parameter value MUST be the text for either an
      IANA-registered media type or a non-standard media type.

   Example:

       ATTACH;FMTTYPE=application/msword:ftp://example.com/pub/docs/
        agenda.doc

3.2.9.  Free/Busy Time Type

   Parameter Name:  FBTYPE

   Purpose:  To specify the free or busy time type.

   Format Definition:  This property parameter is defined by the
      following notation:

       fbtypeparam        = "FBTYPE" "=" ("FREE" / "BUSY"
                          / "BUSY-UNAVAILABLE" / "BUSY-TENTATIVE"
                          / x-name
                ; Some experimental iCalendar free/busy type.
                          / iana-token)
                ; Some other IANA-registered iCalendar free/busy type.

   Description:  This parameter specifies the free or busy time type.
      The value FREE indicates that the time interval is free for
      scheduling.  The value BUSY indicates that the time interval is
      busy because one or more events have been scheduled for that
      interval.  The value BUSY-UNAVAILABLE indicates that the time
      interval is busy and that the interval can not be scheduled.  The
      value BUSY-TENTATIVE indicates that the time interval is busy
      because one or more events have been tentatively scheduled for
      that interval.  If not specified on a property that allows this
      parameter, the default is BUSY.  Applications MUST treat x-name
      and iana-token values they don't recognize the same way as they
      would the BUSY value.

   Example:  The following is an example of this parameter on a
      "FREEBUSY" property.

       FREEBUSY;FBTYPE=BUSY:19980415T133000Z/19980415T170000Z









Desruisseaux                Standards Track                    [Page 20]

RFC 5545                       iCalendar                  September 2009


3.2.10.  Language

   Parameter Name:  LANGUAGE

   Purpose:  To specify the language for text values in a property or
      property parameter.

   Format Definition:  This property parameter is defined by the
      following notation:

       languageparam = "LANGUAGE" "=" language

       language = Language-Tag
                  ; As defined in [RFC5646].

   Description:  This parameter identifies the language of the text in
      the property value and of all property parameter values of the
      property.  The value of the "LANGUAGE" property parameter is that
      defined in [RFC5646].

      For transport in a MIME entity, the Content-Language header field
      can be used to set the default language for the entire body part.
      Otherwise, no default language is assumed.

   Example:  The following are examples of this parameter on the
      "SUMMARY" and "LOCATION" properties:

       SUMMARY;LANGUAGE=en-US:Company Holiday Party

       LOCATION;LANGUAGE=en:Germany

       LOCATION;LANGUAGE=no:Tyskland

3.2.11.  Group or List Membership

   Parameter Name:  MEMBER

   Purpose:  To specify the group or list membership of the calendar
      user specified by the property.

   Format Definition:  This property parameter is defined by the
      following notation:

       memberparam        = "MEMBER" "=" DQUOTE cal-address DQUOTE
                            *("," DQUOTE cal-address DQUOTE)






Desruisseaux                Standards Track                    [Page 21]

RFC 5545                       iCalendar                  September 2009


   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  The parameter identifies the groups or
      list membership for the calendar user specified by the property.
      The parameter value is either a single calendar address in a
      quoted-string or a COMMA-separated list of calendar addresses,
      each in a quoted-string.  The individual calendar address
      parameter values MUST each be specified in a quoted-string.

   Example:

       ATTENDEE;MEMBER="mailto:ietf-calsch@example.org":mailto:
        jsmith@example.com

       ATTENDEE;MEMBER="mailto:projectA@example.com","mailto:pr
        ojectB@example.com":mailto:janedoe@example.com

3.2.12.  Participation Status

   Parameter Name:  PARTSTAT

   Purpose:  To specify the participation status for the calendar user
      specified by the property.

   Format Definition:  This property parameter is defined by the
      following notation:

       partstatparam    = "PARTSTAT" "="
                         (partstat-event
                        / partstat-todo
                        / partstat-jour)

       partstat-event   = ("NEEDS-ACTION"    ; Event needs action
                        / "ACCEPTED"         ; Event accepted
                        / "DECLINED"         ; Event declined
                        / "TENTATIVE"        ; Event tentatively
                                             ; accepted
                        / "DELEGATED"        ; Event delegated
                        / x-name             ; Experimental status
                        / iana-token)        ; Other IANA-registered
                                             ; status
       ; These are the participation statuses for a "VEVENT".
       ; Default is NEEDS-ACTION.

       partstat-todo    = ("NEEDS-ACTION"    ; To-do needs action
                        / "ACCEPTED"         ; To-do accepted
                        / "DECLINED"         ; To-do declined
                        / "TENTATIVE"        ; To-do tentatively
                                             ; accepted



Desruisseaux                Standards Track                    [Page 22]

RFC 5545                       iCalendar                  September 2009


                        / "DELEGATED"        ; To-do delegated
                        / "COMPLETED"        ; To-do completed
                                             ; COMPLETED property has
                                             ; DATE-TIME completed
                        / "IN-PROCESS"       ; To-do in process of
                                             ; being completed
                        / x-name             ; Experimental status
                        / iana-token)        ; Other IANA-registered
                                             ; status
       ; These are the participation statuses for a "VTODO".
       ; Default is NEEDS-ACTION.



       partstat-jour    = ("NEEDS-ACTION"    ; Journal needs action
                        / "ACCEPTED"         ; Journal accepted
                        / "DECLINED"         ; Journal declined
                        / x-name             ; Experimental status
                        / iana-token)        ; Other IANA-registered
                                             ; status
       ; These are the participation statuses for a "VJOURNAL".
       ; Default is NEEDS-ACTION.

   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  The parameter identifies the
      participation status for the calendar user specified by the
      property value.  The parameter values differ depending on whether
      they are associated with a group-scheduled "VEVENT", "VTODO", or
      "VJOURNAL".  The values MUST match one of the values allowed for
      the given calendar component.  If not specified on a property that
      allows this parameter, the default value is NEEDS-ACTION.
      Applications MUST treat x-name and iana-token values they don't
      recognize the same way as they would the NEEDS-ACTION value.

   Example:

       ATTENDEE;PARTSTAT=DECLINED:mailto:jsmith@example.com

3.2.13.  Recurrence Identifier Range

   Parameter Name:  RANGE

   Purpose:  To specify the effective range of recurrence instances from
      the instance specified by the recurrence identifier specified by
      the property.

   Format Definition:  This property parameter is defined by the
      following notation:



Desruisseaux                Standards Track                    [Page 23]

RFC 5545                       iCalendar                  September 2009


       rangeparam = "RANGE" "=" "THISANDFUTURE"
       ; To specify the instance specified by the recurrence identifier
       ; and all subsequent recurrence instances.

   Description:  This parameter can be specified on a property that
      specifies a recurrence identifier.  The parameter specifies the
      effective range of recurrence instances that is specified by the
      property.  The effective range is from the recurrence identifier
      specified by the property.  If this parameter is not specified on
      an allowed property, then the default range is the single instance
      specified by the recurrence identifier value of the property.  The
      parameter value can only be "THISANDFUTURE" to indicate a range
      defined by the recurrence identifier and all subsequent instances.
      The value "THISANDPRIOR" is deprecated by this revision of
      iCalendar and MUST NOT be generated by applications.

   Example:

       RECURRENCE-ID;RANGE=THISANDFUTURE:19980401T133000Z

3.2.14.  Alarm Trigger Relationship

   Parameter Name:  RELATED

   Purpose:  To specify the relationship of the alarm trigger with
      respect to the start or end of the calendar component.

   Format Definition:  This property parameter is defined by the
      following notation:

       trigrelparam       = "RELATED" "="
                           ("START"       ; Trigger off of start
                          / "END")        ; Trigger off of end

   Description:  This parameter can be specified on properties that
      specify an alarm trigger with a "DURATION" value type.  The
      parameter specifies whether the alarm will trigger relative to the
      start or end of the calendar component.  The parameter value START
      will set the alarm to trigger off the start of the calendar
      component; the parameter value END will set the alarm to trigger
      off the end of the calendar component.  If the parameter is not
      specified on an allowable property, then the default is START.

   Example:

       TRIGGER;RELATED=END:PT5M





Desruisseaux                Standards Track                    [Page 24]

RFC 5545                       iCalendar                  September 2009


3.2.15.  Relationship Type

   Parameter Name:  RELTYPE

   Purpose:  To specify the type of hierarchical relationship associated
      with the calendar component specified by the property.

   Format Definition:  This property parameter is defined by the
      following notation:

       reltypeparam       = "RELTYPE" "="
                           ("PARENT"    ; Parent relationship - Default
                          / "CHILD"     ; Child relationship
                          / "SIBLING"   ; Sibling relationship
                          / iana-token  ; Some other IANA-registered
                                        ; iCalendar relationship type
                          / x-name)     ; A non-standard, experimental
                                        ; relationship type

   Description:  This parameter can be specified on a property that
      references another related calendar.  The parameter specifies the
      hierarchical relationship type of the calendar component
      referenced by the property.  The parameter value can be PARENT, to
      indicate that the referenced calendar component is a superior of
      calendar component; CHILD to indicate that the referenced calendar
      component is a subordinate of the calendar component; or SIBLING
      to indicate that the referenced calendar component is a peer of
      the calendar component.  If this parameter is not specified on an
      allowable property, the default relationship type is PARENT.
      Applications MUST treat x-name and iana-token values they don't
      recognize the same way as they would the PARENT value.

   Example:

       RELATED-TO;RELTYPE=SIBLING:19960401-080045-4000F192713@
        example.com

3.2.16.  Participation Role

   Parameter Name:  ROLE

   Purpose:  To specify the participation role for the calendar user
      specified by the property.

   Format Definition:  This property parameter is defined by the
      following notation:





Desruisseaux                Standards Track                    [Page 25]

RFC 5545                       iCalendar                  September 2009


       roleparam  = "ROLE" "="
                   ("CHAIR"             ; Indicates chair of the
                                        ; calendar entity
                  / "REQ-PARTICIPANT"   ; Indicates a participant whose
                                        ; participation is required
                  / "OPT-PARTICIPANT"   ; Indicates a participant whose
                                        ; participation is optional
                  / "NON-PARTICIPANT"   ; Indicates a participant who
                                        ; is copied for information
                                        ; purposes only
                  / x-name              ; Experimental role
                  / iana-token)         ; Other IANA role
       ; Default is REQ-PARTICIPANT

   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  The parameter specifies the participation
      role for the calendar user specified by the property in the group
      schedule calendar component.  If not specified on a property that
      allows this parameter, the default value is REQ-PARTICIPANT.
      Applications MUST treat x-name and iana-token values they don't
      recognize the same way as they would the REQ-PARTICIPANT value.

   Example:

       ATTENDEE;ROLE=CHAIR:mailto:mrbig@example.com

3.2.17.  RSVP Expectation

   Parameter Name:  RSVP

   Purpose:  To specify whether there is an expectation of a favor of a
      reply from the calendar user specified by the property value.

   Format Definition:  This property parameter is defined by the
      following notation:

       rsvpparam = "RSVP" "=" ("TRUE" / "FALSE")
       ; Default is FALSE

   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  The parameter identifies the expectation
      of a reply from the calendar user specified by the property value.
      This parameter is used by the "Organizer" to request a
      participation status reply from an "Attendee" of a group-scheduled
      event or to-do.  If not specified on a property that allows this
      parameter, the default value is FALSE.





Desruisseaux                Standards Track                    [Page 26]

RFC 5545                       iCalendar                  September 2009


   Example:

       ATTENDEE;RSVP=TRUE:mailto:jsmith@example.com

3.2.18.  Sent By

   Parameter Name:  SENT-BY

   Purpose:  To specify the calendar user that is acting on behalf of
      the calendar user specified by the property.

   Format Definition:  This property parameter is defined by the
      following notation:

       sentbyparam        = "SENT-BY" "=" DQUOTE cal-address DQUOTE

   Description:  This parameter can be specified on properties with a
      CAL-ADDRESS value type.  The parameter specifies the calendar user
      that is acting on behalf of the calendar user specified by the
      property.  The parameter value MUST be a mailto URI as defined in
      [RFC2368].  The individual calendar address parameter values MUST
      each be specified in a quoted-string.

   Example:

       ORGANIZER;SENT-BY="mailto:sray@example.com":mailto:
        jsmith@example.com

3.2.19.  Time Zone Identifier

   Parameter Name:  TZID

   Purpose:  To specify the identifier for the time zone definition for
      a time component in the property value.

   Format Definition:  This property parameter is defined by the
      following notation:

       tzidparam  = "TZID" "=" [tzidprefix] paramtext

       tzidprefix = "/"

   Description:  This parameter MUST be specified on the "DTSTART",
      "DTEND", "DUE", "EXDATE", and "RDATE" properties when either a
      DATE-TIME or TIME value type is specified and when the value is
      neither a UTC or a "floating" time.  Refer to the DATE-TIME or
      TIME value type definition for a description of UTC and "floating
      time" formats.  This property parameter specifies a text value



Desruisseaux                Standards Track                    [Page 27]

RFC 5545                       iCalendar                  September 2009


      that uniquely identifies the "VTIMEZONE" calendar component to be
      used when evaluating the time portion of the property.  The value
      of the "TZID" property parameter will be equal to the value of the
      "TZID" property for the matching time zone definition.  An
      individual "VTIMEZONE" calendar component MUST be specified for
      each unique "TZID" parameter value specified in the iCalendar
      object.

      The parameter MUST be specified on properties with a DATE-TIME
      value if the DATE-TIME is not either a UTC or a "floating" time.
      Failure to include and follow VTIMEZONE definitions in iCalendar
      objects may lead to inconsistent understanding of the local time
      at any given location.

      The presence of the SOLIDUS character as a prefix, indicates that
      this "TZID" represents a unique ID in a globally defined time zone
      registry (when such registry is defined).

         Note: This document does not define a naming convention for
         time zone identifiers.  Implementers may want to use the naming
         conventions defined in existing time zone specifications such
         as the public-domain TZ database [TZDB].  The specification of
         globally unique time zone identifiers is not addressed by this
         document and is left for future study.

      The following are examples of this property parameter:

       DTSTART;TZID=America/New_York:19980119T020000

       DTEND;TZID=America/New_York:19980119T030000

      The "TZID" property parameter MUST NOT be applied to DATE
      properties and DATE-TIME or TIME properties whose time values are
      specified in UTC.

      The use of local time in a DATE-TIME or TIME value without the
      "TZID" property parameter is to be interpreted as floating time,
      regardless of the existence of "VTIMEZONE" calendar components in
      the iCalendar object.

      For more information, see the sections on the value types DATE-
      TIME and TIME.









Desruisseaux                Standards Track                    [Page 28]

RFC 5545                       iCalendar                  September 2009


3.2.20.  Value Data Types

   Parameter Name:  VALUE

   Purpose:  To explicitly specify the value type format for a property
      value.

   Format Definition:  This property parameter is defined by the
      following notation:

       valuetypeparam = "VALUE" "=" valuetype

       valuetype  = ("BINARY"
                  / "BOOLEAN"
                  / "CAL-ADDRESS"
                  / "DATE"
                  / "DATE-TIME"
                  / "DURATION"
                  / "FLOAT"
                  / "INTEGER"
                  / "PERIOD"
                  / "RECUR"
                  / "TEXT"
                  / "TIME"
                  / "URI"
                  / "UTC-OFFSET"
                  / x-name
                  ; Some experimental iCalendar value type.
                  / iana-token)
                  ; Some other IANA-registered iCalendar value type.

   Description:  This parameter specifies the value type and format of
      the property value.  The property values MUST be of a single value
      type.  For example, a "RDATE" property cannot have a combination
      of DATE-TIME and TIME value types.

      If the property's value is the default value type, then this
      parameter need not be specified.  However, if the property's
      default value type is overridden by some other allowable value
      type, then this parameter MUST be specified.

      Applications MUST preserve the value data for x-name and iana-
      token values that they don't recognize without attempting to
      interpret or parse the value data.







Desruisseaux                Standards Track                    [Page 29]

RFC 5545                       iCalendar                  September 2009


