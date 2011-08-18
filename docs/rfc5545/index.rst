=========================================================================
Internet Calendaring and Scheduling Core Object Specification (iCalendar)
=========================================================================

Abstract
""""""""

This document defines the iCalendar data format for representing and
exchanging calendaring and scheduling information such as events,
to-dos, journal entries, and free/busy information, independent of any
particular calendar service or protocol.

Status of This Memo
"""""""""""""""""""

This document specifies an Internet standards track protocol for the
Internet community, and requests discussion and suggestions for
improvements.  Please refer to the current edition of the "Internet
Official Protocol Standards" (STD 1) for the standardization state
and status of this protocol.  Distribution of this memo is unlimited.

Copyright and License Notice
""""""""""""""""""""""""""""

Copyright (c) 2009 IETF Trust and the persons identified as the
document authors.  All rights reserved.

This document is subject to BCP 78 and the IETF Trust's Legal
Provisions Relating to IETF Documents
(http://trustee.ietf.org/license-info) in effect on the date of
publication of this document.  Please review these documents
carefully, as they describe your rights and restrictions with respect
to this document.  Code Components extracted from this document must
include Simplified BSD License text as described in Section 4.e of
the Trust Legal Provisions and are provided without warranty as
described in the BSD License.

This document may contain material from IETF Documents or IETF
Contributions published or made publicly available before November
10, 2008.  The person(s) controlling the copyright in some of this
material may not have granted the IETF Trust the right to allow
modifications of such material outside the IETF Standards Process.
Without obtaining an adequate license from the person(s) controlling
the copyright in such materials, this document may not be modified
outside the IETF Standards Process, and derivative works of it may
not be created outside the IETF Standards Process, except to format
it for publication as an RFC or to translate it into languages other
than English.

Table of Contents
"""""""""""""""""

.. toctree::
    :maxdepth: 3

    1_introduction
    2_basic_grammar_and_convetions
    3_icalendar_object_specification.rst

::

      3.2.  Property Parameters . . . . . . . . . . . . . . . . . . .  12
        3.2.1.  Alternate Text Representation . . . . . . . . . . . .  13
        3.2.2.  Common Name . . . . . . . . . . . . . . . . . . . . .  15
        3.2.3.  Calendar User Type  . . . . . . . . . . . . . . . . .  15
        3.2.4.  Delegators  . . . . . . . . . . . . . . . . . . . . .  16
        3.2.5.  Delegatees  . . . . . . . . . . . . . . . . . . . . .  16
        3.2.6.  Directory Entry Reference . . . . . . . . . . . . . .  17
        3.2.7.  Inline Encoding . . . . . . . . . . . . . . . . . . .  17
        3.2.8.  Format Type . . . . . . . . . . . . . . . . . . . . .  18
        3.2.9.  Free/Busy Time Type . . . . . . . . . . . . . . . . .  19
        3.2.10. Language  . . . . . . . . . . . . . . . . . . . . . .  20
        3.2.11. Group or List Membership  . . . . . . . . . . . . . .  20
        3.2.12. Participation Status  . . . . . . . . . . . . . . . .  21
        3.2.13. Recurrence Identifier Range . . . . . . . . . . . . .  22
        3.2.14. Alarm Trigger Relationship  . . . . . . . . . . . . .  23
        3.2.15. Relationship Type . . . . . . . . . . . . . . . . . .  24
        3.2.16. Participation Role  . . . . . . . . . . . . . . . . .  25
        3.2.17. RSVP Expectation  . . . . . . . . . . . . . . . . . .  25
        3.2.18. Sent By . . . . . . . . . . . . . . . . . . . . . . .  26
        3.2.19. Time Zone Identifier  . . . . . . . . . . . . . . . .  26
        3.2.20. Value Data Types  . . . . . . . . . . . . . . . . . .  28
      3.3.  Property Value Data Types . . . . . . . . . . . . . . . .  29
        3.3.1.  Binary  . . . . . . . . . . . . . . . . . . . . . . .  29
        3.3.2.  Boolean . . . . . . . . . . . . . . . . . . . . . . .  30
        3.3.3.  Calendar User Address . . . . . . . . . . . . . . . .  30
        3.3.4.  Date  . . . . . . . . . . . . . . . . . . . . . . . .  31
        3.3.5.  Date-Time . . . . . . . . . . . . . . . . . . . . . .  31
        3.3.6.  Duration  . . . . . . . . . . . . . . . . . . . . . .  34
        3.3.7.  Float . . . . . . . . . . . . . . . . . . . . . . . .  35
        3.3.8.  Integer . . . . . . . . . . . . . . . . . . . . . . .  35
        3.3.9.  Period of Time  . . . . . . . . . . . . . . . . . . .  36
        3.3.10. Recurrence Rule . . . . . . . . . . . . . . . . . . .  37
        3.3.11. Text  . . . . . . . . . . . . . . . . . . . . . . . .  45
        3.3.12. Time  . . . . . . . . . . . . . . . . . . . . . . . .  46
        3.3.13. URI . . . . . . . . . . . . . . . . . . . . . . . . .  48
        3.3.14. UTC Offset  . . . . . . . . . . . . . . . . . . . . .  49
      3.4.  iCalendar Object  . . . . . . . . . . . . . . . . . . . .  49
      3.5.  Property  . . . . . . . . . . . . . . . . . . . . . . . .  50
      3.6.  Calendar Components . . . . . . . . . . . . . . . . . . .  50
        3.6.1.  Event Component . . . . . . . . . . . . . . . . . . .  52
        3.6.2.  To-Do Component . . . . . . . . . . . . . . . . . . .  56
        3.6.3.  Journal Component . . . . . . . . . . . . . . . . . .  58
        3.6.4.  Free/Busy Component . . . . . . . . . . . . . . . . .  60
        3.6.5.  Time Zone Component . . . . . . . . . . . . . . . . .  63
        3.6.6.  Alarm Component . . . . . . . . . . . . . . . . . . .  72
      3.7.  Calendar Properties . . . . . . . . . . . . . . . . . . .  77
        3.7.1.  Calendar Scale  . . . . . . . . . . . . . . . . . . .  77
        3.7.2.  Method  . . . . . . . . . . . . . . . . . . . . . . .  78
        3.7.3.  Product Identifier  . . . . . . . . . . . . . . . . .  79
        3.7.4.  Version . . . . . . . . . . . . . . . . . . . . . . .  80
      3.8.  Component Properties  . . . . . . . . . . . . . . . . . .  81
        3.8.1.  Descriptive Component Properties  . . . . . . . . . .  81
          3.8.1.1.  Attachment  . . . . . . . . . . . . . . . . . . .  81
          3.8.1.2.  Categories  . . . . . . . . . . . . . . . . . . .  82
          3.8.1.3.  Classification  . . . . . . . . . . . . . . . . .  83
          3.8.1.4.  Comment . . . . . . . . . . . . . . . . . . . . .  84
          3.8.1.5.  Description . . . . . . . . . . . . . . . . . . .  85
          3.8.1.6.  Geographic Position . . . . . . . . . . . . . . .  87
          3.8.1.7.  Location  . . . . . . . . . . . . . . . . . . . .  88
          3.8.1.8.  Percent Complete  . . . . . . . . . . . . . . . .  89
          3.8.1.9.  Priority  . . . . . . . . . . . . . . . . . . . .  90
          3.8.1.10. Resources . . . . . . . . . . . . . . . . . . . .  92
          3.8.1.11. Status  . . . . . . . . . . . . . . . . . . . . .  93
          3.8.1.12. Summary . . . . . . . . . . . . . . . . . . . . .  94
        3.8.2.  Date and Time Component Properties  . . . . . . . . .  95
          3.8.2.1.  Date-Time Completed . . . . . . . . . . . . . . .  95
          3.8.2.2.  Date-Time End . . . . . . . . . . . . . . . . . .  96
          3.8.2.3.  Date-Time Due . . . . . . . . . . . . . . . . . .  97
          3.8.2.4.  Date-Time Start . . . . . . . . . . . . . . . . .  99
          3.8.2.5.  Duration  . . . . . . . . . . . . . . . . . . . . 100
          3.8.2.6.  Free/Busy Time  . . . . . . . . . . . . . . . . . 101
          3.8.2.7.  Time Transparency . . . . . . . . . . . . . . . . 102
        3.8.3.  Time Zone Component Properties  . . . . . . . . . . . 103
          3.8.3.1.  Time Zone Identifier  . . . . . . . . . . . . . . 103
          3.8.3.2.  Time Zone Name  . . . . . . . . . . . . . . . . . 105
          3.8.3.3.  Time Zone Offset From . . . . . . . . . . . . . . 106
          3.8.3.4.  Time Zone Offset To . . . . . . . . . . . . . . . 106
          3.8.3.5.  Time Zone URL . . . . . . . . . . . . . . . . . . 107
        3.8.4.  Relationship Component Properties . . . . . . . . . . 108
          3.8.4.1.  Attendee  . . . . . . . . . . . . . . . . . . . . 108
          3.8.4.2.  Contact . . . . . . . . . . . . . . . . . . . . . 111
          3.8.4.3.  Organizer . . . . . . . . . . . . . . . . . . . . 113
          3.8.4.4.  Recurrence ID . . . . . . . . . . . . . . . . . . 114
          3.8.4.5.  Related To  . . . . . . . . . . . . . . . . . . . 117
          3.8.4.6.  Uniform Resource Locator  . . . . . . . . . . . . 118
          3.8.4.7.  Unique Identifier . . . . . . . . . . . . . . . . 119
        3.8.5.  Recurrence Component Properties . . . . . . . . . . . 120
          3.8.5.1.  Exception Date-Times  . . . . . . . . . . . . . . 120
          3.8.5.2.  Recurrence Date-Times . . . . . . . . . . . . . . 122
          3.8.5.3.  Recurrence Rule . . . . . . . . . . . . . . . . . 124
        3.8.6.  Alarm Component Properties  . . . . . . . . . . . . . 134
          3.8.6.1.  Action  . . . . . . . . . . . . . . . . . . . . . 134
          3.8.6.2.  Repeat Count  . . . . . . . . . . . . . . . . . . 135
          3.8.6.3.  Trigger . . . . . . . . . . . . . . . . . . . . . 135
        3.8.7.  Change Management Component Properties  . . . . . . . 138
          3.8.7.1.  Date-Time Created . . . . . . . . . . . . . . . . 138
          3.8.7.2.  Date-Time Stamp . . . . . . . . . . . . . . . . . 139
          3.8.7.3.  Last Modified . . . . . . . . . . . . . . . . . . 140
          3.8.7.4.  Sequence Number . . . . . . . . . . . . . . . . . 141
        3.8.8.  Miscellaneous Component Properties  . . . . . . . . . 142
          3.8.8.1.  IANA Properties . . . . . . . . . . . . . . . . . 142
          3.8.8.2.  Non-Standard Properties . . . . . . . . . . . . . 142
          3.8.8.3.  Request Status  . . . . . . . . . . . . . . . . . 144
    4.  iCalendar Object Examples . . . . . . . . . . . . . . . . . . 146
    5.  Recommended Practices . . . . . . . . . . . . . . . . . . . . 150
    6.  Internationalization Considerations . . . . . . . . . . . . . 151
    7.  Security Considerations . . . . . . . . . . . . . . . . . . . 151
    8.  IANA Considerations . . . . . . . . . . . . . . . . . . . . . 151
      8.1.  iCalendar Media Type Registration . . . . . . . . . . . . 151
      8.2.  New iCalendar Elements Registration . . . . . . . . . . . 155
        8.2.1.  iCalendar Elements Registration Procedure . . . . . . 155
        8.2.2.  Registration Template for Components  . . . . . . . . 155
        8.2.3.  Registration Template for Properties  . . . . . . . . 156
        8.2.4.  Registration Template for Parameters  . . . . . . . . 156
        8.2.5.  Registration Template for Value Data Types  . . . . . 157
        8.2.6.  Registration Template for Values  . . . . . . . . . . 157
      8.3.  Initial iCalendar Elements Registries . . . . . . . . . . 158
        8.3.1.  Components Registry . . . . . . . . . . . . . . . . . 158
        8.3.2.  Properties Registry . . . . . . . . . . . . . . . . . 158
        8.3.3.  Parameters Registry . . . . . . . . . . . . . . . . . 161
        8.3.4.  Value Data Types Registry . . . . . . . . . . . . . . 162
        8.3.5.  Calendar User Types Registry  . . . . . . . . . . . . 162
        8.3.6.  Free/Busy Time Types Registry . . . . . . . . . . . . 163
        8.3.7.  Participation Statuses Registry . . . . . . . . . . . 163
        8.3.8.  Relationship Types Registry . . . . . . . . . . . . . 164
        8.3.9.  Participation Roles Registry  . . . . . . . . . . . . 164
        8.3.10. Actions Registry  . . . . . . . . . . . . . . . . . . 165
        8.3.11. Classifications Registry  . . . . . . . . . . . . . . 165
        8.3.12. Methods Registry  . . . . . . . . . . . . . . . . . . 165
    9.  Acknowledgments . . . . . . . . . . . . . . . . . . . . . . . 165
    10. References  . . . . . . . . . . . . . . . . . . . . . . . . . 166
      10.1. Normative References  . . . . . . . . . . . . . . . . . . 166
      10.2. Informative References  . . . . . . . . . . . . . . . . . 167
    Appendix A.  Differences from RFC 2445  . . . . . . . . . . . . . 169
      A.1.  New Restrictions  . . . . . . . . . . . . . . . . . . . . 169
      A.2.  Restrictions Removed  . . . . . . . . . . . . . . . . . . 169
      A.3.  Deprecated Features . . . . . . . . . . . . . . . . . . . 169

