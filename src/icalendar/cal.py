# -*- coding: utf-8 -*-
"""Calendar is a dictionary like Python object that can render itself as VCAL
files according to rfc2445.

These are the defined components.
"""
from datetime import datetime, timedelta
from icalendar.caselessdict import CaselessDict
from icalendar.parser import Contentline
from icalendar.parser import Contentlines
from icalendar.parser import Parameters
from icalendar.parser import q_join
from icalendar.parser import q_split
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.prop import TypesFactory
from icalendar.prop import vText, vDDDLists
from icalendar.timezone_cache import _timezone_cache

import pytz
import dateutil.rrule, dateutil.tz
from pytz.tzinfo import DstTzInfo

from icalendar.compat import unicode_type


######################################
# The component factory

class ComponentFactory(CaselessDict):
    """All components defined in rfc 2445 are registered in this factory class.
    To get a component you can use it like this.
    """

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict.
        """
        super(ComponentFactory, self).__init__(*args, **kwargs)
        self['VEVENT'] = Event
        self['VTODO'] = Todo
        self['VJOURNAL'] = Journal
        self['VFREEBUSY'] = FreeBusy
        self['VTIMEZONE'] = Timezone
        self['STANDARD'] = TimezoneStandard
        self['DAYLIGHT'] = TimezoneDaylight
        self['VALARM'] = Alarm
        self['VCALENDAR'] = Calendar


# These Properties have multiple property values inlined in one propertyline
# seperated by comma. Use CaselessDict as simple caseless set.
INLINE = CaselessDict({
    'CATEGORIES': 1,
    'RESOURCES': 1,
    'FREEBUSY': 1,
})

_marker = []


class Component(CaselessDict):
    """Component is the base object for calendar, Event and the other
    components defined in RFC 2445. normally you will not use this class
    directy, but rather one of the subclasses.
    """

    name = None         # should be defined in each component
    required = ()       # These properties are required
    singletons = ()     # These properties must only appear once
    multiple = ()       # may occur more than once
    exclusive = ()      # These properties are mutually exclusive
    inclusive = ()      # if any occurs the other(s) MUST occur
                        # ('duration', 'repeat')
    ignore_exceptions = False   # if True, and we cannot parse this
                                # component, we will silently ignore
                                # it, rather than let the exception
                                # propagate upwards
    # not_compliant = ['']  # List of non-compliant properties.

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict.
        """
        super(Component, self).__init__(*args, **kwargs)
        # set parameters here for properties that use non-default values
        self.subcomponents = []  # Components can be nested.
        self.errors = []  # If we ignored exception(s) while
                          # parsing a property, contains error strings

    # def is_compliant(self, name):
    #    """Returns True is the given property name is compliant with the
    #    icalendar implementation.
    #
    #    If the parser is too strict it might prevent parsing erroneous but
    #    otherwise compliant properties. So the parser is pretty lax, but it is
    #    possible to test for non-complience by calling this method.
    #    """
    #    return name in not_compliant

    def __bool__(self):
        """Returns True, CaselessDict would return False if it had no items.
        """
        return True

    # python 2 compatibility
    __nonzero__ = __bool__

    def is_empty(self):
        """Returns True if Component has no items or subcomponents, else False.
        """
        return True if not (list(self.values()) + self.subcomponents) else False  # noqa

    @property
    def is_broken(self):
        return bool(self.errors)

    #############################
    # handling of property values

    def _encode(self, name, value, parameters=None, encode=1):
        """Encode values to icalendar property values.

        :param name: Name of the property.
        :type name: string

        :param value: Value of the property. Either of a basic Python type of
                      any of the icalendar's own property types.
        :type value: Python native type or icalendar property type.

        :param parameters: Property parameter dictionary for the value. Only
                           available, if encode is set to True.
        :type parameters: Dictionary

        :param encode: True, if the value should be encoded to one of
                       icalendar's own property types (Fallback is "vText")
                       or False, if not.
        :type encode: Boolean

        :returns: icalendar property value
        """
        if not encode:
            return value
        if isinstance(value, types_factory.all_types):
            # Don't encode already encoded values.
            return value
        klass = types_factory.for_property(name)
        obj = klass(value)
        if parameters:
            if isinstance(parameters, dict):
                params = Parameters()
                for key, item in parameters.items():
                    params[key] = item
                parameters = params
            assert isinstance(parameters, Parameters)
            obj.params = parameters
        return obj

    def add(self, name, value, parameters=None, encode=1):
        """Add a property.

        :param name: Name of the property.
        :type name: string

        :param value: Value of the property. Either of a basic Python type of
                      any of the icalendar's own property types.
        :type value: Python native type or icalendar property type.

        :param parameters: Property parameter dictionary for the value. Only
                           available, if encode is set to True.
        :type parameters: Dictionary

        :param encode: True, if the value should be encoded to one of
                       icalendar's own property types (Fallback is "vText")
                       or False, if not.
        :type encode: Boolean

        :returns: None
        """
        if isinstance(value, datetime) and\
                name.lower() in ('dtstamp', 'created', 'last-modified'):
            # RFC expects UTC for those... force value conversion.
            if getattr(value, 'tzinfo', False) and value.tzinfo is not None:
                value = value.astimezone(pytz.utc)
            else:
                # assume UTC for naive datetime instances
                value = pytz.utc.localize(value)

        # encode value
        if encode and isinstance(value, list) \
                and name.lower() not in ['rdate', 'exdate', 'categories']:
            # Individually convert each value to an ical type except rdate and
            # exdate, where lists of dates might be passed to vDDDLists.
            value = [self._encode(name, v, parameters, encode) for v in value]
        else:
            value = self._encode(name, value, parameters, encode)

        # set value
        if name in self:
            # If property already exists, append it.
            oldval = self[name]
            if isinstance(oldval, list):
                if isinstance(value, list):
                    value = oldval + value
                else:
                    oldval.append(value)
                    value = oldval
            else:
                value = [oldval, value]
        self[name] = value

    def _decode(self, name, value):
        """Internal for decoding property values.
        """

        # TODO: Currently the decoded method calls the icalendar.prop instances
        # from_ical. We probably want to decode properties into Python native
        # types here. But when parsing from an ical string with from_ical, we
        # want to encode the string into a real icalendar.prop property.
        if isinstance(value, vDDDLists):
            # TODO: Workaround unfinished decoding
            return value
        decoded = types_factory.from_ical(name, value)
        # TODO: remove when proper decoded is implemented in every prop.* class
        # Workaround to decode vText properly
        if isinstance(decoded, vText):
            decoded = decoded.encode(DEFAULT_ENCODING)
        return decoded

    def decoded(self, name, default=_marker):
        """Returns decoded value of property.
        """
        # XXX: fail. what's this function supposed to do in the end?
        # -rnix

        if name in self:
            value = self[name]
            if isinstance(value, list):
                return [self._decode(name, v) for v in value]
            return self._decode(name, value)
        else:
            if default is _marker:
                raise KeyError(name)
            else:
                return default

    ########################################################################
    # Inline values. A few properties have multiple values inlined in in one
    # property line. These methods are used for splitting and joining these.

    def get_inline(self, name, decode=1):
        """Returns a list of values (split on comma).
        """
        vals = [v.strip('" ') for v in q_split(self[name])]
        if decode:
            return [self._decode(name, val) for val in vals]
        return vals

    def set_inline(self, name, values, encode=1):
        """Converts a list of values into comma seperated string and sets value
        to that.
        """
        if encode:
            values = [self._encode(name, value, encode=1) for value in values]
        self[name] = types_factory['inline'](q_join(values))

    #########################
    # Handling of components

    def add_component(self, component):
        """Add a subcomponent to this component.
        """
        self.subcomponents.append(component)

    def _walk(self, name):
        """Walk to given component.
        """
        result = []
        if name is None or self.name == name:
            result.append(self)
        for subcomponent in self.subcomponents:
            result += subcomponent._walk(name)
        return result

    def walk(self, name=None):
        """Recursively traverses component and subcomponents. Returns sequence
        of same. If name is passed, only components with name will be returned.
        """
        if name is not None:
            name = name.upper()
        return self._walk(name)

    #####################
    # Generation

    def property_items(self, recursive=True, sorted=True):
        """Returns properties in this component and subcomponents as:
        [(name, value), ...]
        """
        vText = types_factory['text']
        properties = [('BEGIN', vText(self.name).to_ical())]
        if sorted:
            property_names = self.sorted_keys()
        else:
            property_names = self.keys()

        for name in property_names:
            values = self[name]
            if isinstance(values, list):
                # normally one property is one line
                for value in values:
                    properties.append((name, value))
            else:
                properties.append((name, values))
        if recursive:
            # recursion is fun!
            for subcomponent in self.subcomponents:
                properties += subcomponent.property_items(sorted=sorted)
        properties.append(('END', vText(self.name).to_ical()))
        return properties

    @classmethod
    def from_ical(cls, st, multiple=False):
        """Populates the component recursively from a string.
        """
        stack = []  # a stack of components
        comps = []
        for line in Contentlines.from_ical(st):  # raw parsing
            if not line:
                continue

            try:
                name, params, vals = line.parts()
            except ValueError as e:
                # if unable to parse a line within a component
                # that ignores exceptions, mark the component
                # as broken and skip the line. otherwise raise.
                component = stack[-1] if stack else None
                if not component or not component.ignore_exceptions:
                    raise
                component.errors.append((None, unicode_type(e)))
                continue

            uname = name.upper()
            # check for start of component
            if uname == 'BEGIN':
                # try and create one of the components defined in the spec,
                # otherwise get a general Components for robustness.
                c_name = vals.upper()
                c_class = component_factory.get(c_name, Component)
                # If component factory cannot resolve ``c_name``, the generic
                # ``Component`` class is used which does not have the name set.
                # That's opposed to the usage of ``cls``, which represents a
                # more concrete subclass with a name set (e.g. VCALENDAR).
                component = c_class()
                if not getattr(component, 'name', ''):  # undefined components
                    component.name = c_name
                stack.append(component)
            # check for end of event
            elif uname == 'END':
                # we are done adding properties to this component
                # so pop it from the stack and add it to the new top.
                component = stack.pop()
                if not stack:  # we are at the end
                    comps.append(component)
                else:
                    stack[-1].add_component(component)
                if vals == 'VTIMEZONE' and \
                        'TZID' in component and \
                        component['TZID'] not in pytz.all_timezones and \
                        component['TZID'] not in _timezone_cache:
                    _timezone_cache[component['TZID']] = component.to_tz()
            # we are adding properties to the current top of the stack
            else:
                factory = types_factory.for_property(name)
                component = stack[-1] if stack else None
                if not component:
                    raise ValueError('Property "{prop}" does not have '
                                     'a parent component.'.format(prop=name))
                datetime_names = ('DTSTART', 'DTEND', 'RECURRENCE-ID', 'DUE',
                                  'FREEBUSY', 'RDATE', 'EXDATE')
                try:
                    if name in datetime_names and 'TZID' in params:
                        vals = factory(factory.from_ical(vals, params['TZID']))
                    else:
                        vals = factory(factory.from_ical(vals))
                except ValueError as e:
                    if not component.ignore_exceptions:
                        raise
                    component.errors.append((uname, unicode_type(e)))
                    component.add(name, None, encode=0)
                else:
                    vals.params = params
                    component.add(name, vals, encode=0)

        if multiple:
            return comps
        if len(comps) > 1:
            raise ValueError('Found multiple components where '
                             'only one is allowed: {st!r}'.format(**locals()))
        if len(comps) < 1:
            raise ValueError('Found no components where '
                             'exactly one is required: '
                             '{st!r}'.format(**locals()))
        return comps[0]

    def content_line(self, name, value, sorted=True):
        """Returns property as content line.
        """
        params = getattr(value, 'params', Parameters())
        return Contentline.from_parts(name, params, value, sorted=sorted)

    def content_lines(self, sorted=True):
        """Converts the Component and subcomponents into content lines.
        """
        contentlines = Contentlines()
        for name, value in self.property_items(sorted=sorted):
            cl = self.content_line(name, value, sorted=sorted)
            contentlines.append(cl)
        contentlines.append('')  # remember the empty string in the end
        return contentlines

    def to_ical(self, sorted=True):
        '''
        :param sorted: Whether parameters and properties should be
                       lexicographically sorted.
        '''

        content_lines = self.content_lines(sorted=sorted)
        return content_lines.to_ical()

    def __repr__(self):
        """String representation of class with all of it's subcomponents.
        """
        subs = ', '.join([str(it) for it in self.subcomponents])
        return '%s(%s%s)' % (
            self.name or type(self).__name__,
            dict(self),
            ', %s' % subs if subs else ''
        )


#######################################
# components defined in RFC 5545

class Event(Component):

    name = 'VEVENT'

    canonical_order = (
        'SUMMARY', 'DTSTART', 'DTEND', 'DURATION', 'DTSTAMP',
        'UID', 'RECURRENCE-ID', 'SEQUENCE', 'RRULE', 'RDATE',
        'EXDATE',
    )

    required = ('UID', 'DTSTAMP',)
    singletons = (
        'CLASS', 'CREATED', 'DESCRIPTION', 'DTSTART', 'GEO', 'LAST-MODIFIED',
        'LOCATION', 'ORGANIZER', 'PRIORITY', 'DTSTAMP', 'SEQUENCE', 'STATUS',
        'SUMMARY', 'TRANSP', 'URL', 'RECURRENCE-ID', 'DTEND', 'DURATION',
        'UID', 'CATEGORIES',
    )
    exclusive = ('DTEND', 'DURATION',)
    multiple = (
        'ATTACH', 'ATTENDEE', 'COMMENT', 'CONTACT', 'EXDATE',
        'RSTATUS', 'RELATED', 'RESOURCES', 'RDATE', 'RRULE'
    )
    ignore_exceptions = True


class Todo(Component):

    name = 'VTODO'

    required = ('UID', 'DTSTAMP',)
    singletons = (
        'CLASS', 'COMPLETED', 'CREATED', 'DESCRIPTION', 'DTSTAMP', 'DTSTART',
        'GEO', 'LAST-MODIFIED', 'LOCATION', 'ORGANIZER', 'PERCENT-COMPLETE',
        'PRIORITY', 'RECURRENCE-ID', 'SEQUENCE', 'STATUS', 'SUMMARY', 'UID',
        'URL', 'DUE', 'DURATION',
    )
    exclusive = ('DUE', 'DURATION',)
    multiple = (
        'ATTACH', 'ATTENDEE', 'CATEGORIES', 'COMMENT', 'CONTACT', 'EXDATE',
        'RSTATUS', 'RELATED', 'RESOURCES', 'RDATE', 'RRULE'
    )


class Journal(Component):

    name = 'VJOURNAL'

    required = ('UID', 'DTSTAMP',)
    singletons = (
        'CLASS', 'CREATED', 'DTSTART', 'DTSTAMP', 'LAST-MODIFIED', 'ORGANIZER',
        'RECURRENCE-ID', 'SEQUENCE', 'STATUS', 'SUMMARY', 'UID', 'URL',
    )
    multiple = (
        'ATTACH', 'ATTENDEE', 'CATEGORIES', 'COMMENT', 'CONTACT', 'EXDATE',
        'RELATED', 'RDATE', 'RRULE', 'RSTATUS', 'DESCRIPTION',
    )


class FreeBusy(Component):

    name = 'VFREEBUSY'

    required = ('UID', 'DTSTAMP',)
    singletons = (
        'CONTACT', 'DTSTART', 'DTEND', 'DTSTAMP', 'ORGANIZER',
        'UID', 'URL',
    )
    multiple = ('ATTENDEE', 'COMMENT', 'FREEBUSY', 'RSTATUS',)


class Timezone(Component):
    name = 'VTIMEZONE'
    canonical_order = ('TZID',)
    required = ('TZID',) # it also requires one of components DAYLIGHT and STANDARD
    singletons = ('TZID', 'LAST-MODIFIED', 'TZURL',)

    @staticmethod
    def _extract_offsets(component, tzname):
        """extract offsets and transition times from a VTIMEZONE component
        :param component: a STANDARD or DAYLIGHT component
        :param tzname: the name of the zone
        """
        offsetfrom = component['TZOFFSETFROM'].td
        offsetto = component['TZOFFSETTO'].td
        dtstart = component['DTSTART'].dt

        # offsets need to be rounded to the next minute, we might loose up
        # to 30 seconds accuracy, but it can't be helped (datetime
        # supposedly cannot handle smaller offsets)
        offsetto_s = int((offsetto.seconds + 30) / 60) * 60
        offsetto = timedelta(days=offsetto.days, seconds=offsetto_s)
        offsetfrom_s = int((offsetfrom.seconds + 30) / 60) * 60
        offsetfrom = timedelta(days=offsetfrom.days, seconds=offsetfrom_s)

        # expand recurrences
        if 'RRULE' in component:
            # to be paranoid about correct weekdays
            # evaluate the rrule with the current offset
            tzi = dateutil.tz.tzoffset ("(offsetfrom)", offsetfrom)
            rrstart = dtstart.replace (tzinfo=tzi)

            rrulestr = component['RRULE'].to_ical().decode('utf-8')
            rrule = dateutil.rrule.rrulestr(rrulestr, dtstart=rrstart)
            if not {'UNTIL', 'COUNT'}.intersection(component['RRULE'].keys()):
                # pytz.timezones don't know any transition dates after 2038
                # either
                rrule._until = datetime(2038, 12, 31, tzinfo=pytz.UTC)

            # constructing the pytz-timezone requires UTC transition times.
            # here we construct local times without tzinfo, the offset to UTC
            # gets subtracted in to_tz().
            transtimes = [dt.replace (tzinfo=None) for dt in rrule]

        # or rdates
        elif 'RDATE' in component:
            if not isinstance(component['RDATE'], list):
                rdates = [component['RDATE']]
            else:
                rdates = component['RDATE']
            transtimes = [dtstart] + [leaf.dt for tree in rdates for
                                      leaf in tree.dts]
        else:
            transtimes = [dtstart]

        transitions = [(transtime, offsetfrom, offsetto, tzname) for
                       transtime in set(transtimes)]

        if component.name == 'STANDARD':
            is_dst = 0
        elif component.name == 'DAYLIGHT':
            is_dst = 1
        return is_dst, transitions

    @staticmethod
    def _make_unique_tzname(tzname, tznames):
        """
        :param tzname: Candidate tzname
        :param tznames: Other tznames
        """
        # TODO better way of making sure tznames are unique
        while tzname in tznames:
            tzname += '_1'
        tznames.add(tzname)
        return tzname

    def to_tz(self):
        """convert this VTIMEZONE component to a pytz.timezone object
        """
        try:
            zone = str(self['TZID'])
        except UnicodeEncodeError:
            zone = self['TZID'].encode('ascii', 'replace')
        transitions = []
        dst = {}
        tznames = set()
        for component in self.walk():
            if type(component) == Timezone:
                continue
            assert isinstance(component['DTSTART'].dt, datetime), (
                "VTIMEZONEs sub-components' DTSTART must be of type datetime, not date"
            )
            try:
                tzname = str(component['TZNAME'])
            except UnicodeEncodeError:
                tzname = component['TZNAME'].encode('ascii', 'replace')
                tzname = self._make_unique_tzname(tzname, tznames)
            except KeyError:
                tzname = '{0}_{1}_{2}_{3}'.format(
                    zone,
                    component['DTSTART'].to_ical().decode('utf-8'),
                    component['TZOFFSETFROM'].to_ical(),  # for whatever reason this is str/unicode
                    component['TZOFFSETTO'].to_ical(),  # for whatever reason this is str/unicode
                )
                tzname = self._make_unique_tzname(tzname, tznames)

            dst[tzname], component_transitions = self._extract_offsets(
                component, tzname
            )
            transitions.extend(component_transitions)

        transitions.sort()
        transition_times = [
            transtime - osfrom for transtime, osfrom, _, _ in transitions
        ]

        # transition_info is a list with tuples in the format
        # (utcoffset, dstoffset, name)
        # dstoffset = 0, if current transition is to standard time
        #           = this_utcoffset - prev_standard_utcoffset, otherwise
        transition_info = []
        for num, (transtime, osfrom, osto, name) in enumerate(transitions):
            dst_offset = False
            if not dst[name]:
                dst_offset = timedelta(seconds=0)
            else:
                # go back in time until we find a transition to dst
                for index in range(num - 1, -1, -1):
                    if not dst[transitions[index][3]]:  # [3] is the name
                        dst_offset = osto - transitions[index][2]  # [2] is osto  # noqa
                        break
                # when the first transition is to dst, we didn't find anything
                # in the past, so we have to look into the future
                if not dst_offset:
                    for index in range(num, len(transitions)):
                        if not dst[transitions[index][3]]:  # [3] is the name
                            dst_offset = osto - transitions[index][2]  # [2] is osto  # noqa
                            break
            assert dst_offset is not False
            transition_info.append((osto, dst_offset, name))

        cls = type(zone, (DstTzInfo,), {
            'zone': zone,
            '_utc_transition_times': transition_times,
            '_transition_info': transition_info
        })

        return cls()


class TimezoneStandard(Component):
    name = 'STANDARD'
    required = ('DTSTART', 'TZOFFSETTO', 'TZOFFSETFROM')
    singletons = ('DTSTART', 'TZOFFSETTO', 'TZOFFSETFROM',)
    multiple = ('COMMENT', 'RDATE', 'TZNAME', 'RRULE', 'EXDATE')


class TimezoneDaylight(Component):
    name = 'DAYLIGHT'
    required = TimezoneStandard.required
    singletons = TimezoneStandard.singletons
    multiple = TimezoneStandard.multiple


class Alarm(Component):

    name = 'VALARM'
    # some properties MAY/MUST/MUST NOT appear depending on ACTION value
    required = ('ACTION', 'TRIGGER',)
    singletons = (
            'ATTACH', 'ACTION', 'DESCRIPTION', 'SUMMARY', 'TRIGGER',
            'DURATION', 'REPEAT',
            )
    inclusive = (('DURATION', 'REPEAT',), ('SUMMARY', 'ATTENDEE',))
    multiple = ('ATTENDEE', 'ATTACH')


class Calendar(Component):
    """This is the base object for an iCalendar file.
    """
    name = 'VCALENDAR'
    canonical_order = ('VERSION', 'PRODID', 'CALSCALE', 'METHOD',)
    required = ('PRODID', 'VERSION', )
    singletons = ('PRODID', 'VERSION', 'CALSCALE', 'METHOD')

# These are read only singleton, so one instance is enough for the module
types_factory = TypesFactory()
component_factory = ComponentFactory()
