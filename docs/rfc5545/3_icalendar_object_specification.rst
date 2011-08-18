3. iCalendar Object Specification
=================================

The following sections define the details of a Calendaring and
Scheduling Core Object Specification.  The Calendaring and Scheduling
Core Object is a collection of calendaring and scheduling
information.  Typically, this information will consist of an
iCalendar stream with one or more iCalendar objects.  The body of the
iCalendar object consists of a sequence of calendar properties and
one or more calendar components.

Section 3.1 defines the content line format; Section 3.2 defines the
property parameter format; Section 3.3 defines the data types for
property values; Section 3.4 defines the iCalendar object format;
Section 3.5 defines the iCalendar property format; Section 3.6
defines the calendar component format; Section 3.7 defines calendar
properties; and Section 3.8 defines calendar component properties.

This information is intended to be an integral part of the MIME
content type registration.  In addition, this information can be used
independent of such content registration.  In particular, this memo
has direct applicability for use as a calendaring and scheduling
exchange format in file-, memory-, or network-based transport
mechanisms.


.. toctree::
    :maxdepth: 2

    3_1_content_lines.rst
    3_2_property_parameters.rst
