3.1 Content Lines
=================

The iCalendar object is organized into individual lines of text,
called content lines.  Content lines are delimited by a line break,
which is a CRLF sequence (CR character followed by LF character).

Lines of text SHOULD NOT be longer than 75 octets, excluding the line
break.  Long content lines SHOULD be split into a multiple line
representations using a line "folding" technique.  That is, a long
line can be split between any two characters by inserting a CRLF
immediately followed by a single linear white-space character (i.e.,
SPACE or HTAB).  Any sequence of CRLF followed immediately by a
single linear white-space character is ignored (i.e., removed) when
processing the content type.

For example, the line::

  DESCRIPTION:This is a long description that exists on a long line.

Can be represented as::

  DESCRIPTION:This is a lo
   ng description
    that exists on a long line.

The process of moving from this folded multiple-line representation
to its single-line representation is called "unfolding".  Unfolding
is accomplished by removing the CRLF and the linear white-space
character that immediately follows.

When parsing a content line, folded lines MUST first be unfolded
according to the unfolding procedure described above.

.. note::

    It is possible for very simple implementations to generate
    improperly folded lines in the middle of a UTF-8 multi-octet
    sequence.  For this reason, implementations need to unfold lines
    in such a way to properly restore the original sequence.

The content information associated with an iCalendar object is
formatted using a syntax similar to that defined by [RFC2425].  That
is, the content information consists of CRLF-separated content lines.

The following notation defines the lines of content in an iCalendar
object::

     contentline   = name *(";" param ) ":" value CRLF
     ; This ABNF is just a general definition for an initial parsing
     ; of the content line into its property name, parameter list,
     ; and value string

     ; When parsing a content line, folded lines MUST first
     ; be unfolded according to the unfolding procedure
     ; described above.  When generating a content line, lines
     ; longer than 75 octets SHOULD be folded according to
     ; the folding procedure described above.

     name          = iana-token / x-name

     iana-token    = 1*(ALPHA / DIGIT / "-")
     ; iCalendar identifier registered with IANA

     x-name        = "X-" [vendorid "-"] 1*(ALPHA / DIGIT / "-")
     ; Reserved for experimental use.

     vendorid      = 3*(ALPHA / DIGIT)
     ; Vendor identification

     param         = param-name "=" param-value *("," param-value)
     ; Each property defines the specific ABNF for the parameters
     ; allowed on the property.  Refer to specific properties for
     ; precise parameter ABNF.

     param-name    = iana-token / x-name

     param-value   = paramtext / quoted-string

     paramtext     = *SAFE-CHAR

     value         = *VALUE-CHAR

     quoted-string = DQUOTE *QSAFE-CHAR DQUOTE

     QSAFE-CHAR    = WSP / %x21 / %x23-7E / NON-US-ASCII
     ; Any character except CONTROL and DQUOTE

     SAFE-CHAR     = WSP / %x21 / %x23-2B / %x2D-39 / %x3C-7E
                   / NON-US-ASCII
     ; Any character except CONTROL, DQUOTE, ";", ":", ","

     VALUE-CHAR    = WSP / %x21-7E / NON-US-ASCII
     ; Any textual character

     NON-US-ASCII  = UTF8-2 / UTF8-3 / UTF8-4
     ; UTF8-2, UTF8-3, and UTF8-4 are defined in [RFC3629]

     CONTROL       = %x00-08 / %x0A-1F / %x7F
     ; All the controls except HTAB

The property value component of a content line has a format that is
property specific.  Refer to the section describing each property for
a definition of this format.

All names of properties, property parameters, enumerated property
values and property parameter values are case-insensitive.  However,
all other property values are case-sensitive, unless otherwise
stated.


3.1.1. List and Field Separators
--------------------------------

Some properties and parameters allow a list of values.  Values in a
list of values MUST be separated by a COMMA character.  There is no
significance to the order of values in a list.  For those parameter
values (such as those that specify URI values) that are specified in
quoted-strings, the individual quoted-strings are separated by a
COMMA character.

Some property values are defined in terms of multiple parts.  These
structured property values MUST have their value parts separated by a
SEMICOLON character.

Some properties allow a list of parameters.  Each property parameter
in a list of property parameters MUST be separated by a SEMICOLON
character.

Property parameters with values containing a COLON character, a
SEMICOLON character or a COMMA character MUST be placed in quoted
text.

For example, in the following properties, a SEMICOLON is used to
separate property parameters from each other and a COMMA character is
used to separate property values in a value list.

::

  ATTENDEE;RSVP=TRUE;ROLE=REQ-PARTICIPANT:mailto:
   jsmith@example.com

  RDATE;VALUE=DATE:19970304,19970504,19970704,19970904


3.1.2. Multiple Values
----------------------

Some properties defined in the iCalendar object can have multiple
values.  The general rule for encoding multi-valued items is to
simply create a new content line for each value, including the
property name.  However, it should be noted that some properties
support encoding multiple values in a single property by separating
the values with a COMMA character.  Individual property definitions
should be consulted for determining whether a specific property
allows multiple values and in which of these two forms.  Multi-valued
properties MUST NOT be used to specify multiple language variants of
the same value.  Calendar applications SHOULD display all values.


3.1.3. Binary Content
---------------------

Binary content information in an iCalendar object SHOULD be
referenced using a URI within a property value.  That is, the binary
content information SHOULD be placed in an external MIME entity that
can be referenced by a URI from within the iCalendar object.  In
applications where this is not feasible, binary content information
can be included within an iCalendar object, but only after first
encoding it into text using the "BASE64" encoding method defined in
[RFC4648].  Inline binary content SHOULD only be used in applications
whose special circumstances demand that an iCalendar object be
expressed as a single entity.  A property containing inline binary
content information MUST specify the "ENCODING" property parameter.
Binary content information placed external to the iCalendar object
MUST be referenced by a uniform resource identifier (URI).

The following example specifies an "ATTACH" property that references
an attachment external to the iCalendar object with a URI reference::

  ATTACH:http://example.com/public/quarterly-report.doc

The following example specifies an "ATTACH" property with inline
binary encoded content information::

  ATTACH;FMTTYPE=text/plain;ENCODING=BASE64;VALUE=BINARY:VGhlIH
   F1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4


3.1.4. Character Set
--------------------

There is not a property parameter to declare the charset used in a
property value.  The default charset for an iCalendar stream is UTF-8
as defined in [RFC3629].

The "charset" Content-Type parameter MUST be used in MIME transports
to specify the charset being used.
