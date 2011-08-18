1. Introduction
===============

The use of calendaring and scheduling has grown considerably in the
last decade.  Enterprise and inter-enterprise business has become
dependent on rapid scheduling of events and actions using this
information technology.  This memo is intended to progress the level
of interoperability possible between dissimilar calendaring and
scheduling applications.  This memo defines a MIME content type for
exchanging electronic calendaring and scheduling information.  The
Internet Calendaring and Scheduling Core Object Specification, or
iCalendar, allows for the capture and exchange of information
normally stored within a calendaring and scheduling application; such
as a Personal Information Manager (PIM) or a Group-Scheduling
product.

The iCalendar format is suitable as an exchange format between
applications or systems.  The format is defined in terms of a MIME
content type.  This will enable the object to be exchanged using
several transports, including but not limited to SMTP, HTTP, a file
system, desktop interactive protocols such as the use of a memory-
based clipboard or drag/drop interactions, point-to-point
asynchronous communication, wired-network transport, or some form of
unwired transport such as infrared.

The memo also provides for the definition of iCalendar object methods
that will map this content type to a set of messages for supporting
calendaring and scheduling operations such as requesting, replying
to, modifying, and canceling meetings or appointments, to-dos, and
journal entries.  The iCalendar object methods can be used to define
other calendaring and scheduling operations such as requesting for
and replying with free/busy time data.  Such a scheduling protocol is
defined in the iCalendar Transport-independent Interoperability
Protocol (iTIP) defined in [2446bis].

The memo also includes a formal grammar for the content type based on
the Internet ABNF defined in [RFC5234].  This ABNF is required for
the implementation of parsers and to serve as the definitive
reference when ambiguities or questions arise in interpreting the
descriptive prose definition of the memo.  Additional restrictions
that could not easily be expressed with the ABNF syntax are specified
as comments in the ABNF.  Comments with normative statements should
be treated as such.

