# -*- coding: utf-8 -*-
"""This module parses and generates contentlines as defined in RFC 2445
(iCalendar), but will probably work for other MIME types with similar syntax.
Eg. RFC 2426 (vCard)

It is stupid in the sense that it treats the content purely as strings. No type
conversion is attempted.
"""
import re
import logging
from icalendar import DEFAULT_ENCODING
from icalendar import SEQUENCE_TYPES
from icalendar.caselessdict import CaselessDict


logger = logging.getLogger('icalendar')


def safe_unicode(value, encoding='utf-8'):
    """Converts a value to unicode, even if it is already a unicode string.

    """
    if isinstance(value, unicode):
        return value
    elif isinstance(value, basestring):
        try:
            value = unicode(value, encoding)
        except (UnicodeDecodeError):
            value = value.decode('utf-8', 'replace')
    return value


def escape_char(text):
    """Format value according to iCalendar TEXT escaping rules.
    """
    # NOTE: ORDER MATTERS!
    return text.replace('\N', '\n')\
               .replace('\\', '\\\\')\
               .replace(';', r'\;')\
               .replace(',', r'\,')\
               .replace('\r\n', r'\n')\
               .replace('\n', r'\n')


def unescape_char(text):
    # NOTE: ORDER MATTERS!
    return text.replace(r'\N', r'\n')\
               .replace(r'\r\n', '\n')\
               .replace(r'\n', '\n')\
               .replace(r'\,', ',')\
               .replace(r'\;', ';')\
               .replace('\\\\', '\\')


def tzid_from_dt(dt):
    tzid = None
    if hasattr(dt.tzinfo, 'zone'):
        tzid = dt.tzinfo.zone  # pytz implementation
    elif hasattr(dt.tzinfo, 'tzname'):
        try:
            tzid = dt.tzinfo.tzname(dt)  # dateutil implementation
        except AttributeError:
            # No tzid available
            pass
    return tzid


def foldline(text, length=75, newline='\r\n'):
    """Make a string folded per RFC5545 (each line must be less than 75 octets)
    """
    assert isinstance(text, str)
#    text.decode('utf-8')  # try to decode, to be sure it's utf-8 or ASCII
    l_line = len(text)
    new_lines = []
    start = 0
    while True:
        end = start + length - 1
        chunk = text[start:end]
        m = NEWLINE.search(chunk)
        if m is not None and m.end() != l_line:
            new_lines.append(text[start:start + m.start()])
            start += m.end()
            continue

        if end >= l_line:
            end = l_line
        else:
            # Check that we don't fold in the middle of a UTF-8 character:
            # http://lists.osafoundation.org/pipermail/ietf-calsify/2006-August/001126.html
            while True:
                char_value = ord(text[end])
                if char_value < 128 or char_value >= 192:
                    # This is not in the middle of a UTF-8 character, so we
                    # can fold here:
                    break
                else:
                    end -= 1

        # Recompute the chunk, since start or end may have changed.
        chunk = text[start:end]
        new_lines.append(chunk)
        if end == l_line:
            break  # Done
        start = end
    return (newline + ' ').join(new_lines).rstrip(' ')

#    return newline.join(
#            icalendar.tools.wrap(text, length,
#                subsequent_indent=' ',
#                drop_whitespace=False,
#                break_long_words=True,
#                replace_whitespace=False
#                )
#            )


#################################################################
# Property parameter stuff

def paramVal(val):
    """Returns a parameter value.
    """
    if type(val) in SEQUENCE_TYPES:
        return q_join(val)
    return dQuote(val)


# Could be improved
NAME = re.compile('[\w-]+')
UNSAFE_CHAR = re.compile('[\x00-\x08\x0a-\x1f\x7F",:;]')
QUNSAFE_CHAR = re.compile('[\x00-\x08\x0a-\x1f\x7F"]')
FOLD = re.compile('(\r?\n)+[ \t]')
NEWLINE = re.compile(r'\r?\n')


def validate_token(name):
    match = NAME.findall(name)
    if len(match) == 1 and name == match[0]:
        return
    raise ValueError(name)


def validate_param_value(value, quoted=True):
    validator = QUNSAFE_CHAR if quoted else UNSAFE_CHAR
    if validator.findall(value):
        raise ValueError(value)


# chars presence of which in parameter value will be cause the value
# to be enclosed in double-quotes
QUOTABLE = re.compile("[,;: ’']")


def dQuote(val):
    """Parameter values containing [,;:] must be double quoted.
    """
    # a double-quote character is forbidden to appear in a parameter value
    # so replace it with a single-quote character
    val = val.replace('"', "'")
    if QUOTABLE.search(val):
        return '"%s"' % val
    return val


# parsing helper
def q_split(st, sep=','):
    """Splits a string on char, taking double (q)uotes into considderation.
    """
    result = []
    cursor = 0
    length = len(st)
    inquote = 0
    for i in range(length):
        ch = st[i]
        if ch == '"':
            inquote = not inquote
        if not inquote and ch == sep:
            result.append(st[cursor:i])
            cursor = i + 1
        if i + 1 == length:
            result.append(st[cursor:])
    return result


def q_join(lst, sep=','):
    """Joins a list on sep, quoting strings with QUOTABLE chars.
    """
    return sep.join(dQuote(itm) for itm in lst)


class Parameters(CaselessDict):
    """
    Parser and generator of Property parameter strings. It knows nothing of
    datatypes. Its main concern is textual structure.
    """

    def params(self):
        """
        in rfc2445 keys are called parameters, so this is to be consitent with
        the naming conventions
        """
        return self.keys()

# TODO?
# Later, when I get more time... need to finish this off now. The last major
# thing missing.
#   def _encode(self, name, value, cond=1):
#       # internal, for conditional convertion of values.
#       if cond:
#           klass = types_factory.for_property(name)
#           return klass(value)
#       return value
#
#   def add(self, name, value, encode=0):
#       "Add a parameter value and optionally encode it."
#       if encode:
#           value = self._encode(name, value, encode)
#       self[name] = value
#
#   def decoded(self, name):
#       "returns a decoded value, or list of same"

    def __repr__(self):
        return 'Parameters(' + dict.__repr__(self) + ')'

    def to_ical(self):
        result = []
        items = self.items()
        items.sort()  # To make doctests work
        for key, value in items:
            value = paramVal(value)
            if isinstance(value, unicode):
                value = value.encode(DEFAULT_ENCODING)
            result.append('%s=%s' % (key.upper(), value))
        return ';'.join(result)

    @staticmethod
    def from_ical(st, strict=False):
        "Parses the parameter format from ical text format"

        # parse into strings
        result = Parameters()
        for param in q_split(st, ';'):
            try:
                key, val = q_split(param, '=')
                validate_token(key)
                # Property parameter values that are not in quoted
                # strings are case insensitive.
                vals = []
                for v in q_split(val, ','):
                    if v.startswith('"') and v.endswith('"'):
                        v = v.strip('"')
                        validate_param_value(v, quoted=True)
                        vals.append(v)
                    else:
                        validate_param_value(v, quoted=False)
                        if strict:
                            vals.append(v.upper())
                        else:
                            vals.append(v)
                if not vals:
                    result[key] = val
                else:
                    if len(vals) == 1:
                        result[key] = vals[0]
                    else:
                        result[key] = vals
            except ValueError as exc:
                raise ValueError('%r is not a valid parameter string: %s'
                                 % (param, exc))
        return result


def escape_string(val):
    assert isinstance(val, str)
    # '%{:02X}'.format(i)
    return val.replace(r'\,', '%2C').replace(r'\:', '%3A')\
              .replace(r'\;', '%3B').replace(r'\\', '%5C')


def unsescape_string(val):
    assert isinstance(val, str)
    return val.replace('%2C', ',').replace('%3A', ':')\
              .replace('%3B', ';').replace('%5C', '\\')


#########################################
# parsing and generation of content lines

class Contentline(str):
    """A content line is basically a string that can be folded and parsed into
    parts.
    """
    def __new__(cls, value, strict=False):
        if isinstance(value, unicode):
            value = value.encode(DEFAULT_ENCODING)
        self = super(Contentline, cls).__new__(cls, value)
        self.strict = strict
        return self

    @staticmethod
    def from_parts(parts):
        """Turn a tuple of parts into a content line.
        """
        (name, params, values) = parts
        try:
            if hasattr(values, 'to_ical'):
                values = values.to_ical()
            else:
                values = vText(values).to_ical()
            # elif isinstance(values, basestring):
            #    values = escape_char(values)

            if params:
                return Contentline('%s;%s:%s'
                                   % (name, params.to_ical(), values))
            return Contentline('%s:%s' % (name, values))
        except Exception as exc:
            logger.error(str(exc))
            raise ValueError(u'Property: %r Wrong values "%r" or "%r"'
                             % (name, params, values))

    def parts(self):
        """Split the content line up into (name, parameters, values) parts.
        """
        try:
            st = escape_string(self)
            name_split = None
            value_split = None
            inquotes = 0
            for i, ch in enumerate(st):
                if not inquotes:
                    if ch in ':;' and not name_split:
                        name_split = i
                    if ch == ':' and not value_split:
                        value_split = i
                if ch == '"':
                    inquotes = not inquotes
            name = unsescape_string(st[:name_split])
            if not name:
                raise ValueError('Key name is required')
            validate_token(name)
            if name_split + 1 == value_split:
                raise ValueError('Invalid content line')
            params = Parameters.from_ical(st[name_split + 1: value_split],
                                          strict=self.strict)
            params = dict((unsescape_string(key), unsescape_string(value))
                          for key, value in params.iteritems())
            values = unsescape_string(st[value_split + 1:])
            return (name, params, values)
        except ValueError as exc:
            raise ValueError("Content line could not be parsed into parts: %r:"
                             " %s" % (self, exc))

    @staticmethod
    def from_ical(st, strict=False):
        """Unfold the content lines in an iCalendar into long content lines.
        """
        try:
            # a fold is carriage return followed by either a space or a tab
            return Contentline(FOLD.sub('', st), strict=strict)
        except:
            raise ValueError('Expected StringType with content line')

    def to_ical(self):
        """Long content lines are folded so they are less than 75 characters.
        wide.
        """
        return foldline(self, newline='\r\n')


class Contentlines(list):
    """I assume that iCalendar files generally are a few kilobytes in size.
    Then this should be efficient. for Huge files, an iterator should probably
    be used instead.
    """
    def to_ical(self):
        """Simply join self.
        """
        return '\r\n'.join(l.to_ical() for l in self if l) + '\r\n'

    @staticmethod
    def from_ical(st):
        """Parses a string into content lines.
        """
        try:
            # a fold is carriage return followed by either a space or a tab
            unfolded = FOLD.sub('', st)
            lines = [Contentline(line) for
                     line in unfolded.splitlines() if line]
            lines.append('')  # '\r\n' at the end of every content line
            return Contentlines(lines)
        except:
            raise ValueError('Expected StringType with content lines')


# ran this:
#    sample = open('./samples/test.ics', 'rb').read() # binary file in windows!
#    lines = Contentlines.from_ical(sample)
#    for line in lines[:-1]:
#        print line.parts()

# got this:
# ('BEGIN', Parameters({}), 'VCALENDAR')
# ('METHOD', Parameters({}), 'Request')
# ('PRODID', Parameters({}), '-//My product//mxm.dk/')
# ('VERSION', Parameters({}), '2.0')
# ('BEGIN', Parameters({}), 'VEVENT')
# ('DESCRIPTION', Parameters({}), 'This is a very long description that ...')
# ('PARTICIPANT', Parameters({'CN': 'Max M'}), 'MAILTO:maxm@mxm.dk')
# ('DTEND', Parameters({}), '20050107T160000')
# ('DTSTART', Parameters({}), '20050107T120000')
# ('SUMMARY', Parameters({}), 'A second event')
# ('END', Parameters({}), 'VEVENT')
# ('BEGIN', Parameters({}), 'VEVENT')
# ('DTEND', Parameters({}), '20050108T235900')
# ('DTSTART', Parameters({}), '20050108T230000')
# ('SUMMARY', Parameters({}), 'A single event')
# ('UID', Parameters({}), '42')
# ('END', Parameters({}), 'VEVENT')
# ('END', Parameters({}), 'VCALENDAR')

# XXX: what kind of hack is this? import depends to be at end
from icalendar.prop import vText
