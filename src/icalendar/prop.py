# -*- coding: utf-8 -*-
"""This module contains the parser/generators (or coders/encoders if you
prefer) for the classes/datatypes that are used in iCalendar:

###########################################################################
# This module defines these property value data types and property parameters

4.2 Defined property parameters are:

     ALTREP, CN, CUTYPE, DELEGATED-FROM, DELEGATED-TO, DIR, ENCODING, FMTTYPE,
     FBTYPE, LANGUAGE, MEMBER, PARTSTAT, RANGE, RELATED, RELTYPE, ROLE, RSVP,
     SENT-BY, TZID, VALUE

4.3 Defined value data types are:

    BINARY, BOOLEAN, CAL-ADDRESS, DATE, DATE-TIME, DURATION, FLOAT, INTEGER,
    PERIOD, RECUR, TEXT, TIME, URI, UTC-OFFSET

###########################################################################

iCalendar properties have values. The values are strongly typed. This module
defines these types, calling val.to_ical() on them will render them as defined
in rfc2445.

If you pass any of these classes a Python primitive, you will have an object
that can render itself as iCalendar formatted date.

Property Value Data Types start with a 'v'. they all have an to_ical() and
from_ical() method. The to_ical() method generates a text string in the
iCalendar format. The from_ical() method can parse this format and return a
primitive Python datatype. So it should always be true that:

    x == vDataType.from_ical(VDataType(x).to_ical())

These types are mainly used for parsing and file generation. But you can set
them directly.
"""
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from datetime import tzinfo

try:
    from dateutil.tz import tzutc
except ImportError:
    tzutc = None

from icalendar import compat
from icalendar.caselessdict import CaselessDict
from icalendar.parser import Parameters
from icalendar.parser import escape_char
from icalendar.parser import tzid_from_dt
from icalendar.parser import unescape_char
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.parser_tools import SEQUENCE_TYPES
from icalendar.parser_tools import to_unicode
from icalendar.timezone_cache import _timezone_cache
from icalendar.windows_to_olson import WINDOWS_TO_OLSON

import base64
import binascii
import pytz
import re
import time as _time


DATE_PART = r'(\d+)D'
TIME_PART = r'T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
DATETIME_PART = '(?:%s)?(?:%s)?' % (DATE_PART, TIME_PART)
WEEKS_PART = r'(\d+)W'
DURATION_REGEX = re.compile(r'([-+]?)P(?:%s|%s)$'
                            % (WEEKS_PART, DATETIME_PART))
WEEKDAY_RULE = re.compile(r'(?P<signal>[+-]?)(?P<relative>[\d]?)'
                          r'(?P<weekday>[\w]{2})$')


####################################################
# handy tzinfo classes you can use.
#

ZERO = timedelta(0)
HOUR = timedelta(hours=1)
STDOFFSET = timedelta(seconds=-_time.timezone)
if _time.daylight:
    DSTOFFSET = timedelta(seconds=-_time.altzone)
else:
    DSTOFFSET = STDOFFSET
DSTDIFF = DSTOFFSET - STDOFFSET


class FixedOffset(tzinfo):
    """Fixed offset in minutes east from UTC.
    """
    def __init__(self, offset, name):
        self.__offset = timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO


class LocalTimezone(tzinfo):
    """Timezone of the machine where the code is running.
    """
    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return ZERO

    def tzname(self, dt):
        return _time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = _time.mktime(tt)
        tt = _time.localtime(stamp)
        return tt.tm_isdst > 0


class vBinary(object):
    """Binary property values are base 64 encoded.
    """

    def __init__(self, obj):
        self.obj = to_unicode(obj)
        self.params = Parameters(encoding='BASE64', value="BINARY")

    def __repr__(self):
        return "vBinary('%s')" % self.to_ical()

    def to_ical(self):
        return binascii.b2a_base64(self.obj.encode('utf-8'))[:-1]

    @staticmethod
    def from_ical(ical):
        try:
            return base64.b64decode(ical)
        except UnicodeError:
            raise ValueError('Not valid base 64 encoding.')


class vBoolean(int):
    """Returns specific string according to state.
    """
    BOOL_MAP = CaselessDict({'true': True, 'false': False})

    def __new__(cls, *args, **kwargs):
        self = super(vBoolean, cls).__new__(cls, *args, **kwargs)
        self.params = Parameters()
        return self

    def to_ical(self):
        if self:
            return b'TRUE'
        return b'FALSE'

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls.BOOL_MAP[ical]
        except Exception:
            raise ValueError("Expected 'TRUE' or 'FALSE'. Got %s" % ical)


class vCalAddress(compat.unicode_type):
    """This just returns an unquoted string.
    """
    def __new__(cls, value, encoding=DEFAULT_ENCODING):
        value = to_unicode(value, encoding=encoding)
        self = super(vCalAddress, cls).__new__(cls, value)
        self.params = Parameters()
        return self

    def __repr__(self):
        return "vCalAddress('%s')" % self.to_ical()

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical):
        return cls(ical)


class vFloat(float):
    """Just a float.
    """
    def __new__(cls, *args, **kwargs):
        self = super(vFloat, cls).__new__(cls, *args, **kwargs)
        self.params = Parameters()
        return self

    def to_ical(self):
        return compat.unicode_type(self).encode('utf-8')

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical)
        except Exception:
            raise ValueError('Expected float value, got: %s' % ical)


class vInt(int):
    """Just an int.
    """
    def __new__(cls, *args, **kwargs):
        self = super(vInt, cls).__new__(cls, *args, **kwargs)
        self.params = Parameters()
        return self

    def to_ical(self):
        return compat.unicode_type(self).encode('utf-8')

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical)
        except Exception:
            raise ValueError('Expected int, got: %s' % ical)


class vDDDLists(object):
    """A list of vDDDTypes values.
    """
    def __init__(self, dt_list):
        if not hasattr(dt_list, '__iter__'):
            dt_list = [dt_list]
        vDDD = []
        tzid = None
        for dt in dt_list:
            dt = vDDDTypes(dt)
            vDDD.append(dt)
            if 'TZID' in dt.params:
                tzid = dt.params['TZID']

        if tzid:
            # NOTE: no support for multiple timezones here!
            self.params = Parameters({'TZID': tzid})
        self.dts = vDDD

    def to_ical(self):
        dts_ical = (dt.to_ical() for dt in self.dts)
        return b",".join(dts_ical)

    @staticmethod
    def from_ical(ical, timezone=None):
        out = []
        ical_dates = ical.split(",")
        for ical_dt in ical_dates:
            out.append(vDDDTypes.from_ical(ical_dt, timezone=timezone))
        return out

class vCategory(object):

    def __init__(self, c_list):
        if not hasattr(c_list, '__iter__'):
            c_list = [c_list]
        self.cats = [vText(c) for c in c_list]

    def to_ical(self):
        return b",".join([c.to_ical() for c in self.cats])

    @staticmethod
    def from_ical(ical):
        ical = to_unicode(ical)
        out = unescape_char(ical).split(',')
        return out


class vDDDTypes(object):
    """A combined Datetime, Date or Duration parser/generator. Their format
    cannot be confused, and often values can be of either types.
    So this is practical.
    """
    def __init__(self, dt):
        if not isinstance(dt, (datetime, date, timedelta, time, tuple)):
            raise ValueError('You must use datetime, date, timedelta, '
                             'time or tuple (for periods)')
        if isinstance(dt, datetime):
            self.params = Parameters({'value': 'DATE-TIME'})
        elif isinstance(dt, date):
            self.params = Parameters({'value': 'DATE'})
        elif isinstance(dt, time):
            self.params = Parameters({'value': 'TIME'})
        elif isinstance(dt, tuple):
            self.params = Parameters({'value': 'PERIOD'})

        if (isinstance(dt, datetime) or isinstance(dt, time))\
                and getattr(dt, 'tzinfo', False):
            tzinfo = dt.tzinfo
            if tzinfo is not pytz.utc and\
               (tzutc is None or not isinstance(tzinfo, tzutc)):
                # set the timezone as a parameter to the property
                tzid = tzid_from_dt(dt)
                if tzid:
                    self.params.update({'TZID': tzid})
        self.dt = dt

    def to_ical(self):
        dt = self.dt
        if isinstance(dt, datetime):
            return vDatetime(dt).to_ical()
        elif isinstance(dt, date):
            return vDate(dt).to_ical()
        elif isinstance(dt, timedelta):
            return vDuration(dt).to_ical()
        elif isinstance(dt, time):
            return vTime(dt).to_ical()
        elif isinstance(dt, tuple) and len(dt) == 2:
            return vPeriod(dt).to_ical()
        else:
            raise ValueError('Unknown date type: {}'.format(type(dt)))

    @classmethod
    def from_ical(cls, ical, timezone=None):
        if isinstance(ical, cls):
            return ical.dt
        u = ical.upper()
        if u.startswith(('P', '-P', '+P')):
            return vDuration.from_ical(ical)
        if '/' in u:
            return vPeriod.from_ical(ical)

        if len(ical) in (15, 16):
            return vDatetime.from_ical(ical, timezone=timezone)
        elif len(ical) == 8:
            return vDate.from_ical(ical)
        elif len(ical) in (6, 7):
            return vTime.from_ical(ical)
        else:
            raise ValueError(
                "Expected datetime, date, or time, got: '%s'" % ical
            )


class vDate(object):
    """Render and generates iCalendar date format.
    """
    def __init__(self, dt):
        if not isinstance(dt, date):
            raise ValueError('Value MUST be a date instance')
        self.dt = dt
        self.params = Parameters({'value': 'DATE'})

    def to_ical(self):
        s = "%04d%02d%02d" % (self.dt.year, self.dt.month, self.dt.day)
        return s.encode('utf-8')

    @staticmethod
    def from_ical(ical):
        try:
            timetuple = (
                int(ical[:4]),  # year
                int(ical[4:6]),  # month
                int(ical[6:8]),  # day
            )
            return date(*timetuple)
        except Exception:
            raise ValueError('Wrong date format %s' % ical)


class vDatetime(object):
    """Render and generates icalendar datetime format.

    vDatetime is timezone aware and uses the pytz library, an implementation of
    the Olson database in Python. When a vDatetime object is created from an
    ical string, you can pass a valid pytz timezone identifier. When a
    vDatetime object is created from a python datetime object, it uses the
    tzinfo component, if present. Otherwise an timezone-naive object is
    created. Be aware that there are certain limitations with timezone naive
    DATE-TIME components in the icalendar standard.
    """
    def __init__(self, dt):
        self.dt = dt
        self.params = Parameters()

    def to_ical(self):
        dt = self.dt
        tzid = tzid_from_dt(dt)

        s = "%04d%02d%02dT%02d%02d%02d" % (
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second
        )
        if tzid == 'UTC':
            s += "Z"
        elif tzid:
            self.params.update({'TZID': tzid})
        return s.encode('utf-8')

    @staticmethod
    def from_ical(ical, timezone=None):
        tzinfo = None
        if timezone:
            try:
                tzinfo = pytz.timezone(timezone)
            except pytz.UnknownTimeZoneError:
                if timezone in WINDOWS_TO_OLSON:
                    tzinfo = pytz.timezone(WINDOWS_TO_OLSON.get(timezone))
                else:
                    tzinfo = _timezone_cache.get(timezone, None)

        try:
            timetuple = (
                int(ical[:4]),  # year
                int(ical[4:6]),  # month
                int(ical[6:8]),  # day
                int(ical[9:11]),  # hour
                int(ical[11:13]),  # minute
                int(ical[13:15]),  # second
            )
            if tzinfo:
                return tzinfo.localize(datetime(*timetuple))
            elif not ical[15:]:
                return datetime(*timetuple)
            elif ical[15:16] == 'Z':
                return pytz.utc.localize(datetime(*timetuple))
            else:
                raise ValueError(ical)
        except Exception:
            raise ValueError('Wrong datetime format: %s' % ical)


class vDuration(object):
    """Subclass of timedelta that renders itself in the iCalendar DURATION
    format.
    """

    def __init__(self, td):
        if not isinstance(td, timedelta):
            raise ValueError('Value MUST be a timedelta instance')
        self.td = td
        self.params = Parameters()

    def to_ical(self):
        sign = ""
        td = self.td
        if td.days < 0:
            sign = "-"
            td = -td
        timepart = ""
        if td.seconds:
            timepart = "T"
            hours = td.seconds // 3600
            minutes = td.seconds % 3600 // 60
            seconds = td.seconds % 60
            if hours:
                timepart += "%dH" % hours
            if minutes or (hours and seconds):
                timepart += "%dM" % minutes
            if seconds:
                timepart += "%dS" % seconds
        if td.days == 0 and timepart:
            return (compat.unicode_type(sign).encode('utf-8') + b'P' +
                    compat.unicode_type(timepart).encode('utf-8'))
        else:
            return (compat.unicode_type(sign).encode('utf-8') + b'P' +
                    compat.unicode_type(abs(td.days)).encode('utf-8') +
                    b'D' + compat.unicode_type(timepart).encode('utf-8'))

    @staticmethod
    def from_ical(ical):
        try:
            match = DURATION_REGEX.match(ical)
            sign, weeks, days, hours, minutes, seconds = match.groups()
            if weeks:
                value = timedelta(weeks=int(weeks))
            else:
                value = timedelta(days=int(days or 0),
                                  hours=int(hours or 0),
                                  minutes=int(minutes or 0),
                                  seconds=int(seconds or 0))
            if sign == '-':
                value = -value
            return value
        except Exception:
            raise ValueError('Invalid iCalendar duration: %s' % ical)


class vPeriod(object):
    """A precise period of time.
    """
    def __init__(self, per):
        start, end_or_duration = per
        if not (isinstance(start, datetime) or isinstance(start, date)):
            raise ValueError('Start value MUST be a datetime or date instance')
        if not (isinstance(end_or_duration, datetime) or
                isinstance(end_or_duration, date) or
                isinstance(end_or_duration, timedelta)):
            raise ValueError('end_or_duration MUST be a datetime, '
                             'date or timedelta instance')
        by_duration = 0
        if isinstance(end_or_duration, timedelta):
            by_duration = 1
            duration = end_or_duration
            end = start + duration
        else:
            end = end_or_duration
            duration = end - start
        if start > end:
            raise ValueError("Start time is greater than end time")

        self.params = Parameters()
        # set the timezone identifier
        # does not support different timezones for start and end
        tzid = tzid_from_dt(start)
        if tzid:
            self.params['TZID'] = tzid

        self.start = start
        self.end = end
        self.by_duration = by_duration
        self.duration = duration

    def __cmp__(self, other):
        if not isinstance(other, vPeriod):
            raise NotImplementedError('Cannot compare vPeriod with %r' % other)
        return cmp((self.start, self.end), (other.start, other.end))

    def overlaps(self, other):
        if self.start > other.start:
            return other.overlaps(self)
        if self.start <= other.start < self.end:
            return True
        return False

    def to_ical(self):
        if self.by_duration:
            return (vDatetime(self.start).to_ical() + b'/' +
                    vDuration(self.duration).to_ical())
        return (vDatetime(self.start).to_ical() + b'/' +
                vDatetime(self.end).to_ical())

    @staticmethod
    def from_ical(ical):
        try:
            start, end_or_duration = ical.split('/')
            start = vDDDTypes.from_ical(start)
            end_or_duration = vDDDTypes.from_ical(end_or_duration)
            return (start, end_or_duration)
        except Exception:
            raise ValueError('Expected period format, got: %s' % ical)

    def __repr__(self):
        if self.by_duration:
            p = (self.start, self.duration)
        else:
            p = (self.start, self.end)
        return 'vPeriod(%r)' % (p, )


class vWeekday(compat.unicode_type):
    """This returns an unquoted weekday abbrevation.
    """
    week_days = CaselessDict({
        "SU": 0, "MO": 1, "TU": 2, "WE": 3, "TH": 4, "FR": 5, "SA": 6,
    })

    def __new__(cls, value, encoding=DEFAULT_ENCODING):
        value = to_unicode(value, encoding=encoding)
        self = super(vWeekday, cls).__new__(cls, value)
        match = WEEKDAY_RULE.match(self)
        if match is None:
            raise ValueError('Expected weekday abbrevation, got: %s' % self)
        match = match.groupdict()
        sign = match['signal']
        weekday = match['weekday']
        relative = match['relative']
        if weekday not in vWeekday.week_days or sign not in '+-':
            raise ValueError('Expected weekday abbrevation, got: %s' % self)
        self.relative = relative and int(relative) or None
        self.params = Parameters()
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING).upper()

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical.upper())
        except Exception:
            raise ValueError('Expected weekday abbrevation, got: %s' % ical)


class vFrequency(compat.unicode_type):
    """A simple class that catches illegal values.
    """

    frequencies = CaselessDict({
        "SECONDLY": "SECONDLY",
        "MINUTELY": "MINUTELY",
        "HOURLY": "HOURLY",
        "DAILY": "DAILY",
        "WEEKLY": "WEEKLY",
        "MONTHLY": "MONTHLY",
        "YEARLY": "YEARLY",
    })

    def __new__(cls, value, encoding=DEFAULT_ENCODING):
        value = to_unicode(value, encoding=encoding)
        self = super(vFrequency, cls).__new__(cls, value)
        if self not in vFrequency.frequencies:
            raise ValueError('Expected frequency, got: %s' % self)
        self.params = Parameters()
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING).upper()

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical.upper())
        except Exception:
            raise ValueError('Expected frequency, got: %s' % ical)


class vRecur(CaselessDict):
    """Recurrence definition.
    """

    frequencies = ["SECONDLY", "MINUTELY", "HOURLY", "DAILY", "WEEKLY",
                   "MONTHLY", "YEARLY"]

    # Mac iCal ignores RRULEs where FREQ is not the first rule part.
    # Sorts parts according to the order listed in RFC 5545, section 3.3.10.
    canonical_order = ("FREQ", "UNTIL", "COUNT", "INTERVAL",
                       "BYSECOND", "BYMINUTE", "BYHOUR", "BYDAY",
                       "BYMONTHDAY", "BYYEARDAY", "BYWEEKNO", "BYMONTH",
                       "BYSETPOS", "WKST")

    types = CaselessDict({
        'COUNT': vInt,
        'INTERVAL': vInt,
        'BYSECOND': vInt,
        'BYMINUTE': vInt,
        'BYHOUR': vInt,
        'BYWEEKNO': vInt,
        'BYMONTHDAY': vInt,
        'BYYEARDAY': vInt,
        'BYMONTH': vInt,
        'UNTIL': vDDDTypes,
        'BYSETPOS': vInt,
        'WKST': vWeekday,
        'BYDAY': vWeekday,
        'FREQ': vFrequency,
    })

    def __init__(self, *args, **kwargs):
        super(vRecur, self).__init__(*args, **kwargs)
        self.params = Parameters()

    def to_ical(self):
        result = []
        for key, vals in self.sorted_items():
            typ = self.types.get(key, vText)
            if not isinstance(vals, SEQUENCE_TYPES):
                vals = [vals]
            vals = b','.join(typ(val).to_ical() for val in vals)

            # CaselessDict keys are always unicode
            key = key.encode(DEFAULT_ENCODING)
            result.append(key + b'=' + vals)

        return b';'.join(result)

    @classmethod
    def parse_type(cls, key, values):
        # integers
        parser = cls.types.get(key, vText)
        return [parser.from_ical(v) for v in values.split(',')]

    @classmethod
    def from_ical(cls, ical):
        if isinstance(ical, cls):
            return ical
        try:
            recur = cls()
            for pairs in ical.split(';'):
                try:
                    key, vals = pairs.split('=')
                except ValueError:
                    # E.g. incorrect trailing semicolon, like (issue #157):
                    # FREQ=YEARLY;BYMONTH=11;BYDAY=1SU;
                    continue
                recur[key] = cls.parse_type(key, vals)
            return dict(recur)
        except Exception:
            raise ValueError('Error in recurrence rule: %s' % ical)


class vText(compat.unicode_type):
    """Simple text.
    """

    def __new__(cls, value, encoding=DEFAULT_ENCODING):
        value = to_unicode(value, encoding=encoding)
        self = super(vText, cls).__new__(cls, value)
        self.encoding = encoding
        self.params = Parameters()
        return self

    def __repr__(self):
        return "vText('%s')" % self.to_ical()

    def to_ical(self):
        return escape_char(self).encode(self.encoding)

    @classmethod
    def from_ical(cls, ical):
        ical_unesc = unescape_char(ical)
        return cls(ical_unesc)


class vTime(object):
    """Render and generates iCalendar time format.
    """

    def __init__(self, *args):
        if len(args) == 1:
            if not isinstance(args[0], (time, datetime)):
                raise ValueError('Expected a datetime.time, got: %s' % args[0])
            self.dt = args[0]
        else:
            self.dt = time(*args)
        self.params = Parameters({'value': 'TIME'})

    def to_ical(self):
        return self.dt.strftime("%H%M%S")

    @staticmethod
    def from_ical(ical):
        # TODO: timezone support
        try:
            timetuple = (int(ical[:2]), int(ical[2:4]), int(ical[4:6]))
            return time(*timetuple)
        except Exception:
            raise ValueError('Expected time, got: %s' % ical)


class vUri(compat.unicode_type):
    """Uniform resource identifier is basically just an unquoted string.
    """

    def __new__(cls, value, encoding=DEFAULT_ENCODING):
        value = to_unicode(value, encoding=encoding)
        self = super(vUri, cls).__new__(cls, value)
        self.params = Parameters()
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical):
        try:
            return cls(ical)
        except Exception:
            raise ValueError('Expected , got: %s' % ical)


class vGeo(object):
    """A special type that is only indirectly defined in the rfc.
    """

    def __init__(self, geo):
        try:
            latitude, longitude = (geo[0], geo[1])
            latitude = float(latitude)
            longitude = float(longitude)
        except Exception:
            raise ValueError('Input must be (float, float) for '
                             'latitude and longitude')
        self.latitude = latitude
        self.longitude = longitude
        self.params = Parameters()

    def to_ical(self):
        return '%s;%s' % (self.latitude, self.longitude)

    @staticmethod
    def from_ical(ical):
        try:
            latitude, longitude = ical.split(';')
            return (float(latitude), float(longitude))
        except Exception:
            raise ValueError("Expected 'float;float' , got: %s" % ical)


class vUTCOffset(object):
    """Renders itself as a utc offset.
    """

    ignore_exceptions = False   # if True, and we cannot parse this
                                # component, we will silently ignore
                                # it, rather than let the exception
                                # propagate upwards

    def __init__(self, td):
        if not isinstance(td, timedelta):
            raise ValueError('Offset value MUST be a timedelta instance')
        self.td = td
        self.params = Parameters()

    def to_ical(self):

        if self.td < timedelta(0):
            sign = '-%s'
            td = timedelta(0) - self.td  # get timedelta relative to 0
        else:
            # Google Calendar rejects '0000' but accepts '+0000'
            sign = '+%s'
            td = self.td

        days, seconds = td.days, td.seconds

        hours = abs(days * 24 + seconds // 3600)
        minutes = abs((seconds % 3600) // 60)
        seconds = abs(seconds % 60)
        if seconds:
            duration = '%02i%02i%02i' % (hours, minutes, seconds)
        else:
            duration = '%02i%02i' % (hours, minutes)
        return sign % duration

    @classmethod
    def from_ical(cls, ical):
        if isinstance(ical, cls):
            return ical.td
        try:
            sign, hours, minutes, seconds = (ical[0:1],
                                             int(ical[1:3]),
                                             int(ical[3:5]),
                                             int(ical[5:7] or 0))
            offset = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except Exception:
            raise ValueError('Expected utc offset, got: %s' % ical)
        if not cls.ignore_exceptions and offset >= timedelta(hours=24):
            raise ValueError(
                'Offset must be less than 24 hours, was %s' % ical)
        if sign == '-':
            return -offset
        return offset


class vInline(compat.unicode_type):
    """This is an especially dumb class that just holds raw unparsed text and
    has parameters. Conversion of inline values are handled by the Component
    class, so no further processing is needed.
    """
    def __new__(cls, value, encoding=DEFAULT_ENCODING):
        value = to_unicode(value, encoding=encoding)
        self = super(vInline, cls).__new__(cls, value)
        self.params = Parameters()
        return self

    def to_ical(self):
        return self.encode(DEFAULT_ENCODING)

    @classmethod
    def from_ical(cls, ical):
        return cls(ical)


class TypesFactory(CaselessDict):
    """All Value types defined in rfc 2445 are registered in this factory
    class.

    The value and parameter names don't overlap. So one factory is enough for
    both kinds.
    """

    def __init__(self, *args, **kwargs):
        "Set keys to upper for initial dict"
        super(TypesFactory, self).__init__(*args, **kwargs)
        self.all_types = (
            vBinary,
            vBoolean,
            vCalAddress,
            vDDDLists,
            vDDDTypes,
            vDate,
            vDatetime,
            vDuration,
            vFloat,
            vFrequency,
            vGeo,
            vInline,
            vInt,
            vPeriod,
            vRecur,
            vText,
            vTime,
            vUTCOffset,
            vUri,
            vWeekday,
            vCategory,
        )
        self['binary'] = vBinary
        self['boolean'] = vBoolean
        self['cal-address'] = vCalAddress
        self['date'] = vDDDTypes
        self['date-time'] = vDDDTypes
        self['duration'] = vDDDTypes
        self['float'] = vFloat
        self['integer'] = vInt
        self['period'] = vPeriod
        self['recur'] = vRecur
        self['text'] = vText
        self['time'] = vTime
        self['uri'] = vUri
        self['utc-offset'] = vUTCOffset
        self['geo'] = vGeo
        self['inline'] = vInline
        self['date-time-list'] = vDDDLists
        self['categories'] = vCategory

    #################################################
    # Property types

    # These are the default types
    types_map = CaselessDict({
        ####################################
        # Property value types
        # Calendar Properties
        'calscale': 'text',
        'method': 'text',
        'prodid': 'text',
        'version': 'text',
        # Descriptive Component Properties
        'attach': 'uri',
        'categories': 'categories',
        'class': 'text',
        'comment': 'text',
        'description': 'text',
        'geo': 'geo',
        'location': 'text',
        'percent-complete': 'integer',
        'priority': 'integer',
        'resources': 'text',
        'status': 'text',
        'summary': 'text',
        # Date and Time Component Properties
        'completed': 'date-time',
        'dtend': 'date-time',
        'due': 'date-time',
        'dtstart': 'date-time',
        'duration': 'duration',
        'freebusy': 'period',
        'transp': 'text',
        # Time Zone Component Properties
        'tzid': 'text',
        'tzname': 'text',
        'tzoffsetfrom': 'utc-offset',
        'tzoffsetto': 'utc-offset',
        'tzurl': 'uri',
        # Relationship Component Properties
        'attendee': 'cal-address',
        'contact': 'text',
        'organizer': 'cal-address',
        'recurrence-id': 'date-time',
        'related-to': 'text',
        'url': 'uri',
        'uid': 'text',
        # Recurrence Component Properties
        'exdate': 'date-time-list',
        'exrule': 'recur',
        'rdate': 'date-time-list',
        'rrule': 'recur',
        # Alarm Component Properties
        'action': 'text',
        'repeat': 'integer',
        'trigger': 'duration',
        # Change Management Component Properties
        'created': 'date-time',
        'dtstamp': 'date-time',
        'last-modified': 'date-time',
        'sequence': 'integer',
        # Miscellaneous Component Properties
        'request-status': 'text',
        ####################################
        # parameter types (luckily there is no name overlap)
        'altrep': 'uri',
        'cn': 'text',
        'cutype': 'text',
        'delegated-from': 'cal-address',
        'delegated-to': 'cal-address',
        'dir': 'uri',
        'encoding': 'text',
        'fmttype': 'text',
        'fbtype': 'text',
        'language': 'text',
        'member': 'cal-address',
        'partstat': 'text',
        'range': 'text',
        'related': 'text',
        'reltype': 'text',
        'role': 'text',
        'rsvp': 'boolean',
        'sent-by': 'cal-address',
        'tzid': 'text',
        'value': 'text',
    })

    def for_property(self, name):
        """Returns a the default type for a property or parameter
        """
        return self[self.types_map.get(name, 'text')]

    def to_ical(self, name, value):
        """Encodes a named value from a primitive python type to an icalendar
        encoded string.
        """
        type_class = self.for_property(name)
        return type_class(value).to_ical()

    def from_ical(self, name, value):
        """Decodes a named property or parameter value from an icalendar
        encoded string to a primitive python type.
        """
        type_class = self.for_property(name)
        decoded = type_class.from_ical(value)
        return decoded
