# -*- coding: utf-8 -*-
"""Calendar is a dictionary like Python object that can render itself as VCAL
files according to rfc2445.

These are the defined components.
"""
from datetime import datetime
from icalendar.caselessdict import CaselessDict
from icalendar.parser import Contentline
from icalendar.parser import Contentlines
from icalendar.parser import Parameters
from icalendar.parser import q_join
from icalendar.parser import q_split
from icalendar.parser_tools import DEFAULT_ENCODING
from icalendar.parser_tools import data_encode
from icalendar.prop import TypesFactory
from icalendar.prop import vText, vDDDLists

import pytz


######################################
# The component factory

class ComponentFactory(CaselessDict):
    """All components defined in rfc 2445 are registered in this factory class.
    To get a component you can use it like this.
    """

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict.
        """
        CaselessDict.__init__(self, *args, **kwargs)
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
INLINE = CaselessDict(
    [(cat, 1) for cat in ('CATEGORIES', 'RESOURCES', 'FREEBUSY')]
)

_marker = []


class Component(CaselessDict):
    """Component is the base object for calendar, Event and the other
    components defined in RFC 2445. normally you will not use this class
    directy, but rather one of the subclasses.
    """

    name = ''        # must be defined in each component
    required = ()    # These properties are required
    singletons = ()  # These properties must only appear once
    multiple = ()    # may occur more than once
    exclusive = ()   # These properties are mutually exclusive
    inclusive = ()   # if any occurs the other(s) MUST occur
                     # ('duration', 'repeat')
    ignore_exceptions = False   # if True, and we cannot parse this
                                # component, we will silently ignore
                                # it, rather than let the exception
                                # propagate upwards
    # not_compliant = [''] # List of non-compliant properties.

    def __init__(self, *args, **kwargs):
        """Set keys to upper for initial dict.
        """
        CaselessDict.__init__(self, *args, **kwargs)
        # set parameters here for properties that use non-default values
        self.subcomponents = []  # Components can be nested.
        self.is_broken = False  # True if we ignored an exception while
                                # parsing a property

    #def is_compliant(self, name):
    #    """Returns True is the given property name is compliant with the
    #    icalendar implementation.
    #
    #    If the parser is too strict it might prevent parsing erroneous but
    #    otherwise compliant properties. So the parser is pretty lax, but it is
    #    possible to test for non-complience by calling this method.
    #    """
    #    return name in not_compliant

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
                and name.lower() not in ['rdate', 'exdate']:
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
        if not name is None:
            name = name.upper()
        return self._walk(name)

    #####################
    # Generation

    def property_items(self, recursive=True):
        """Returns properties in this component and subcomponents as:
        [(name, value), ...]
        """
        vText = types_factory['text']
        properties = [('BEGIN', vText(self.name).to_ical())]
        property_names = self.sorted_keys()
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
                properties += subcomponent.property_items()
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
            name, params, vals = line.parts()
            uname = name.upper()
            # check for start of component
            if uname == 'BEGIN':
                # try and create one of the components defined in the spec,
                # otherwise get a general Components for robustness.
                c_name = vals.upper()
                c_class = component_factory.get(c_name, cls)
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
                    if not component.is_broken:
                        stack[-1].add_component(component)
            # we are adding properties to the current top of the stack
            else:
                factory = types_factory.for_property(name)
                component = stack[-1]
                datetime_names = ('DTSTART', 'DTEND', 'RECURRENCE-ID', 'DUE',
                                  'FREEBUSY', 'RDATE', 'EXDATE')
                try:
                    if name in datetime_names and 'TZID' in params:
                        vals = factory(factory.from_ical(vals, params['TZID']))
                    else:
                        vals = factory(factory.from_ical(vals))
                except ValueError:
                    if not component.ignore_exceptions:
                        raise
                    component.is_broken = True
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

    def __repr__(self):
        return '%s(%s)' % (self.name, data_encode(self))

    def content_line(self, name, value):
        """Returns property as content line.
        """
        params = getattr(value, 'params', Parameters())
        return Contentline.from_parts(name, params, value)

    def content_lines(self):
        """Converts the Component and subcomponents into content lines.
        """
        contentlines = Contentlines()
        for name, value in self.property_items():
            cl = self.content_line(name, value)
            contentlines.append(cl)
        contentlines.append('')  # remember the empty string in the end
        return contentlines

    def to_ical(self):
        content_lines = self.content_lines()
        return content_lines.to_ical()


#######################################
# components defined in RFC 2445

class Event(Component):

    name = 'VEVENT'

    canonical_order = (
        'SUMMARY', 'DTSTART', 'DTEND', 'DURATION', 'DTSTAMP',
        'UID', 'RECURRENCE-ID', 'SEQUENCE',
        'RRULE' 'EXRULE', 'RDATE', 'EXDATE',
    )

    required = ('UID',)
    singletons = (
        'CLASS', 'CREATED', 'DESCRIPTION', 'DTSTART', 'GEO', 'LAST-MODIFIED',
        'LOCATION', 'ORGANIZER', 'PRIORITY', 'DTSTAMP', 'SEQUENCE', 'STATUS',
        'SUMMARY', 'TRANSP', 'URL', 'RECURRENCE-ID', 'DTEND', 'DURATION',
        'DTSTART',
    )
    exclusive = ('DTEND', 'DURATION', )
    multiple = (
        'ATTACH', 'ATTENDEE', 'CATEGORIES', 'COMMENT', 'CONTACT', 'EXDATE',
        'EXRULE', 'RSTATUS', 'RELATED', 'RESOURCES', 'RDATE', 'RRULE'
    )
    ignore_exceptions = True


class Todo(Component):

    name = 'VTODO'

    required = ('UID',)
    singletons = (
        'CLASS', 'COMPLETED', 'CREATED', 'DESCRIPTION', 'DTSTAMP', 'DTSTART',
        'GEO', 'LAST-MODIFIED', 'LOCATION', 'ORGANIZER', 'PERCENT', 'PRIORITY',
        'RECURRENCE-ID', 'SEQUENCE', 'STATUS', 'SUMMARY', 'UID', 'URL', 'DUE',
        'DURATION',
    )
    exclusive = ('DUE', 'DURATION',)
    multiple = (
        'ATTACH', 'ATTENDEE', 'CATEGORIES', 'COMMENT', 'CONTACT', 'EXDATE',
        'EXRULE', 'RSTATUS', 'RELATED', 'RESOURCES', 'RDATE', 'RRULE'
    )


class Journal(Component):

    name = 'VJOURNAL'

    required = ('UID',)
    singletons = (
        'CLASS', 'CREATED', 'DESCRIPTION', 'DTSTART', 'DTSTAMP',
        'LAST-MODIFIED', 'ORGANIZER', 'RECURRENCE-ID', 'SEQUENCE', 'STATUS',
        'SUMMARY', 'UID', 'URL',
    )
    multiple = (
        'ATTACH', 'ATTENDEE', 'CATEGORIES', 'COMMENT', 'CONTACT', 'EXDATE',
        'EXRULE', 'RELATED', 'RDATE', 'RRULE', 'RSTATUS',
    )


class FreeBusy(Component):

    name = 'VFREEBUSY'

    required = ('UID',)
    singletons = (
        'CONTACT', 'DTSTART', 'DTEND', 'DURATION', 'DTSTAMP', 'ORGANIZER',
        'UID', 'URL',
    )
    multiple = ('ATTENDEE', 'COMMENT', 'FREEBUSY', 'RSTATUS',)


class Timezone(Component):
    name = 'VTIMEZONE'
    canonical_order = ('TZID', 'STANDARD', 'DAYLIGHT',)
    required = ('TZID', 'STANDARD', 'DAYLIGHT',)
    singletons = ('TZID', 'LAST-MODIFIED', 'TZURL',)


class TimezoneStandard(Component):
    name = 'STANDARD'
    required = ('DTSTART', 'TZOFFSETTO', 'TZOFFSETFROM')
    singletons = ('DTSTART', 'TZOFFSETTO', 'TZOFFSETFROM', 'RRULE')
    multiple = ('COMMENT', 'RDATE', 'TZNAME')


class TimezoneDaylight(Component):
    name = 'DAYLIGHT'
    required = ('DTSTART', 'TZOFFSETTO', 'TZOFFSETFROM')
    singletons = ('DTSTART', 'TZOFFSETTO', 'TZOFFSETFROM', 'RRULE')
    multiple = ('COMMENT', 'RDATE', 'TZNAME')


class Alarm(Component):

    name = 'VALARM'
    # not quite sure about these ...
    required = ('ACTION', 'TRIGGER',)
    singletons = ('ATTACH', 'ACTION', 'TRIGGER', 'DURATION', 'REPEAT',)
    inclusive = (('DURATION', 'REPEAT',),)


class Calendar(Component):
    """This is the base object for an iCalendar file.
    """
    name = 'VCALENDAR'
    canonical_order = ('VERSION', 'PRODID', 'CALSCALE', 'METHOD',)
    required = ('prodid', 'version', )
    singletons = ('prodid', 'version', )
    multiple = ('calscale', 'method', )

# These are read only singleton, so one instance is enough for the module
types_factory = TypesFactory()
component_factory = ComponentFactory()
