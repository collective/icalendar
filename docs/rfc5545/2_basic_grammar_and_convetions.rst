2. Basic Grammar and Conventions
================================

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in [RFC2119].

This memo makes use of both a descriptive prose and a more formal
notation for defining the calendaring and scheduling format.

The notation used in this memo is the ABNF notation of [RFC5234].
Readers intending on implementing the format defined in this memo
should be familiar with this notation in order to properly interpret
the specifications of this memo.

All numeric values used in this memo are given in decimal notation.

All names of properties, property parameters, enumerated property
values, and property parameter values are case-insensitive.  However,
all other property values are case-sensitive, unless otherwise
stated.

.. note::
    
    All indented editorial notes, such as this one, are intended
    to provide the reader with additional information.  The
    information is not essential to the building of an implementation
    conformant with this memo.  The information is provided to
    highlight a particular feature or characteristic of the memo.

The format for the iCalendar object is based on the syntax of the
text/directory media type [RFC2425].  While the iCalendar object is
not a profile of the text/directory media type [RFC2425], it does
reuse a number of the elements from the [RFC2425] specification.


2.1. Formatting Conventions
---------------------------

The elements defined in this memo are defined in prose.  Many of the
terms used to describe these have common usage that is different than
the standards usage of this memo.  In order to reference, within this
memo, elements of the calendaring and scheduling model, core object
(this memo), or interoperability protocol [2446bis] some formatting
conventions have been used.  Calendaring and scheduling roles are
referred to in quoted-strings of text with the first character of
each word in uppercase.  For example, "Organizer" refers to a role of
a "Calendar User" within the scheduling protocol defined by
[2446bis].  Calendar components defined by this memo are referred to
with capitalized, quoted-strings of text.  All calendar components
start with the letter "V".  For example, "VEVENT" refers to the event
calendar component, "VTODO" refers to the to-do calendar component,
and "VJOURNAL" refers to the daily journal calendar component.
Scheduling methods defined by iTIP [2446bis] are referred to with
capitalized, quoted-strings of text.  For example, "REQUEST" refers
to the method for requesting a scheduling calendar component be
created or modified, and "REPLY" refers to the method a recipient of
a request uses to update their status with the "Organizer" of the
calendar component.

The properties defined by this memo are referred to with capitalized,
quoted-strings of text, followed by the word "property".  For
example, "ATTENDEE" property refers to the iCalendar property used to
convey the calendar address of a calendar user.  Property parameters
defined by this memo are referred to with lowercase, quoted-strings
of text, followed by the word "parameter".  For example, "value"
parameter refers to the iCalendar property parameter used to override
the default value type for a property value.  Enumerated values
defined by this memo are referred to with capitalized text, either
alone or followed by the word "value".  For example, the "MINUTELY"
value can be used with the "FREQ" component of the "RECUR" value type
to specify repeating components based on an interval of one minute or
more.

The following table lists the different characters from the
[US-ASCII] character set that is referenced in this document.  For
each character, the table specifies the character name used
throughout this document, along with its US-ASCII decimal codepoint.

    ======================  =================
    Character name          Decimal codepoint
    ======================  =================
    HTAB                    9                
    LF                      10               
    CR                      13               
    DQUOTE                  22               
    SPACE                   32               
    PLUS SIGN               43               
    COMMA                   44               
    HYPHEN-MINUS            45               
    PERIOD                  46               
    SOLIDUS                 47               
    COLON                   58               
    SEMICOLON               59               
    LATIN CAPITAL LETTER N  78               
    LATIN CAPITAL LETTER T  84               
    LATIN CAPITAL LETTER X  88               
    LATIN CAPITAL LETTER Z  90               
    BACKSLASH               92               
    LATIN SMALL LETTER N    110              
    ======================  =================


2.2. Related Memos
------------------

Implementers will need to be familiar with several other memos that,
along with this memo, form a framework for Internet calendaring and
scheduling standards.  This memo specifies a core specification of
objects, value types, properties, and property parameters.

* iTIP [2446bis] specifies an interoperability protocol for
  scheduling between different implementations;

* iCalendar Message-Based Interoperability Protocol (iMIP) [2447bis]
  specifies an Internet email binding for [2446bis].

This memo does not attempt to repeat the specification of concepts or
definitions from these other memos.  Where possible, references are
made to the memo that provides for the specification of these
concepts or definitions.

