"""Common functionality between the tests."""

XML_WHITESPACE = "\x09\x0a\x0d\x20"
"""Whitespace is treated differently in XML than in iCalendar.

See:
- Definition: https://www.w3.org/TR/xmlschema-1/#d0e1654
- Credit: https://stackoverflow.com/a/666338
- "White Space: collapse": https://datypic.com/sc/xsd/t-xsd_float.html

"""
