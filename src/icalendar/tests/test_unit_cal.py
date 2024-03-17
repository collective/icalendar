import itertools
from datetime import datetime
from datetime import timedelta
import unittest

import pytest

import icalendar
import pytz
import re
from icalendar.cal import Component, Calendar, Event, ComponentFactory
from icalendar import prop, cal



class TestCalComponent(unittest.TestCase):

    def test_cal_Component(self):

        # A component is like a dictionary with extra methods and attributes.
        c = Component()
        c.name = 'VCALENDAR'

        self.assertTrue(c)
        self.assertTrue(c.is_empty())

        # Every key defines a property.A property can consist of either a
        # single item. This can be set with a single value...
        c['prodid'] = '-//max m//icalendar.mxm.dk/'
        self.assertFalse(c.is_empty())

        self.assertEqual(
            c,
            Calendar({'PRODID': '-//max m//icalendar.mxm.dk/'})
        )

        # or with a list
        c['ATTENDEE'] = ['Max M', 'Rasmussen']
        self.assertEqual(
            c,
            Calendar({'ATTENDEE': ['Max M', 'Rasmussen'],
                      'PRODID': '-//max m//icalendar.mxm.dk/'})
        )

        # ## ADD MULTIPLE VALUES TO A PROPERTY

        # if you use the add method you don't have to considder if a value is
        # a list or not.
        c = Component()
        c.name = 'VEVENT'

        # add multiple values at once
        c.add('attendee',
              ['test@test.com', 'test2@test.com'])

        # or add one per line
        c.add('attendee', 'maxm@mxm.dk')
        c.add('attendee', 'test@example.dk')

        # add again multiple values at once to very concatenaton of lists
        c.add('attendee',
              ['test3@test.com', 'test4@test.com'])

        self.assertEqual(
            c,
            Event({'ATTENDEE': [
                prop.vCalAddress('test@test.com'),
                prop.vCalAddress('test2@test.com'),
                prop.vCalAddress('maxm@mxm.dk'),
                prop.vCalAddress('test@example.dk'),
                prop.vCalAddress('test3@test.com'),
                prop.vCalAddress('test4@test.com')
            ]})
        )

        ###

        # You can get the values back directly ...
        c.add('prodid', '-//my product//')
        self.assertEqual(c['prodid'], prop.vText('-//my product//'))

        # ... or decoded to a python type
        self.assertEqual(c.decoded('prodid'), b'-//my product//')

        # With default values for non existing properties
        self.assertEqual(c.decoded('version', 'No Version'), 'No Version')

        c.add('rdate', [datetime(2013, 3, 28), datetime(2013, 3, 27)])
        self.assertTrue(isinstance(c.decoded('rdate'), prop.vDDDLists))

        # The component can render itself in the RFC 2445 format.
        c = Component()
        c.name = 'VCALENDAR'
        c.add('attendee', 'Max M')
        self.assertEqual(
            c.to_ical(),
            b'BEGIN:VCALENDAR\r\nATTENDEE:Max M\r\nEND:VCALENDAR\r\n'
        )

        # Components can be nested, so You can add a subcomponent. Eg a calendar
        # holds events.
        e = Component(summary='A brief history of time')
        e.name = 'VEVENT'
        e.add('dtend', '20000102T000000', encode=0)
        e.add('dtstart', '20000101T000000', encode=0)
        self.assertEqual(
            e.to_ical(),
            b'BEGIN:VEVENT\r\nDTEND:20000102T000000\r\n'
            + b'DTSTART:20000101T000000\r\nSUMMARY:A brief history of time\r'
            + b'\nEND:VEVENT\r\n'
        )

        c.add_component(e)
        self.assertEqual(
            c.subcomponents,
            [Event({'DTEND': '20000102T000000', 'DTSTART': '20000101T000000',
                    'SUMMARY': 'A brief history of time'})]
        )

        # We can walk over nested componentes with the walk method.
        self.assertEqual([i.name for i in c.walk()], ['VCALENDAR', 'VEVENT'])

        # We can also just walk over specific component types, by filtering
        # them on their name.
        self.assertEqual([i.name for i in c.walk('VEVENT')], ['VEVENT'])

        self.assertEqual(
            [i['dtstart'] for i in c.walk('VEVENT')],
            ['20000101T000000']
        )

        # We can enumerate property items recursively with the property_items
        # method.
        self.assertEqual(
            c.property_items(),
            [('BEGIN', b'VCALENDAR'), ('ATTENDEE', prop.vCalAddress('Max M')),
             ('BEGIN', b'VEVENT'), ('DTEND', '20000102T000000'),
             ('DTSTART', '20000101T000000'),
             ('SUMMARY', 'A brief history of time'), ('END', b'VEVENT'),
             ('END', b'VCALENDAR')]
        )

        # We can also enumerate property items just under the component.
        self.assertEqual(
            c.property_items(recursive=False),
            [('BEGIN', b'VCALENDAR'),
             ('ATTENDEE', prop.vCalAddress('Max M')),
             ('END', b'VCALENDAR')]
        )

        sc = c.subcomponents[0]
        self.assertEqual(
            sc.property_items(recursive=False),
            [('BEGIN', b'VEVENT'), ('DTEND', '20000102T000000'),
             ('DTSTART', '20000101T000000'),
             ('SUMMARY', 'A brief history of time'), ('END', b'VEVENT')]
        )

        # Text fields which span multiple mulitple lines require proper
        # indenting
        c = Calendar()
        c['description'] = 'Paragraph one\n\nParagraph two'
        self.assertEqual(
            c.to_ical(),
            b'BEGIN:VCALENDAR\r\nDESCRIPTION:Paragraph one\\n\\nParagraph two'
            + b'\r\nEND:VCALENDAR\r\n'
        )

        # INLINE properties have their values on one property line. Note the
        # double quoting of the value with a colon in it.
        c = Calendar()
        c['resources'] = 'Chair, Table, "Room: 42"'
        self.assertEqual(
            c,
            Calendar({'RESOURCES': 'Chair, Table, "Room: 42"'})
        )

        self.assertEqual(
            c.to_ical(),
            b'BEGIN:VCALENDAR\r\nRESOURCES:Chair\\, Table\\, "Room: 42"\r\n'
            + b'END:VCALENDAR\r\n'
        )

        # The inline values must be handled by the get_inline() and
        # set_inline() methods.
        self.assertEqual(
            c.get_inline('resources', decode=0),
            ['Chair', 'Table', 'Room: 42']
        )

        # These can also be decoded
        self.assertEqual(
            c.get_inline('resources', decode=1),
            [b'Chair', b'Table', b'Room: 42']
        )

        # You can set them directly ...
        c.set_inline('resources', ['A', 'List', 'of', 'some, recources'],
                     encode=1)
        self.assertEqual(c['resources'], 'A,List,of,"some, recources"')

        # ... and back again
        self.assertEqual(
            c.get_inline('resources', decode=0),
            ['A', 'List', 'of', 'some, recources']
        )

        c['freebusy'] = '19970308T160000Z/PT3H,19970308T200000Z/PT1H,'\
                        + '19970308T230000Z/19970309T000000Z'
        self.assertEqual(
            c.get_inline('freebusy', decode=0),
            ['19970308T160000Z/PT3H', '19970308T200000Z/PT1H',
             '19970308T230000Z/19970309T000000Z']
        )

        freebusy = c.get_inline('freebusy', decode=1)
        self.assertTrue(isinstance(freebusy[0][0], datetime))
        self.assertTrue(isinstance(freebusy[0][1], timedelta))

    def test_cal_Component_add(self):
        # Test the for timezone correctness: dtstart should preserve it's
        # timezone, created, dtstamp and last-modified must be in UTC.
        Component = icalendar.cal.Component
        comp = Component()
        vienna = pytz.timezone("Europe/Vienna")
        comp.add('dtstart', vienna.localize(datetime(2010, 10, 10, 10, 0, 0)))
        comp.add('created', datetime(2010, 10, 10, 12, 0, 0))
        comp.add('dtstamp', vienna.localize(datetime(2010, 10, 10, 14, 0, 0)))
        comp.add('last-modified', pytz.utc.localize(
            datetime(2010, 10, 10, 16, 0, 0)))

        lines = comp.to_ical().splitlines()
        self.assertTrue(
            b"DTSTART;TZID=Europe/Vienna:20101010T100000"
            in lines)
        self.assertTrue(b"CREATED:20101010T120000Z" in lines)
        self.assertTrue(b"DTSTAMP:20101010T120000Z" in lines)
        self.assertTrue(
            b"LAST-MODIFIED:20101010T160000Z" in lines
        )

    def test_cal_Component_add_no_reencode(self):
        """Already encoded values should not be re-encoded.
        """
        comp = cal.Component()
        comp.add('ATTACH', 'me')

        comp.add('ATTACH', 'you', encode=False)
        binary = prop.vBinary('us')
        comp.add('ATTACH', binary)

        self.assertEqual(comp['ATTACH'], ['me', 'you', binary])

    def test_cal_Component_add_property_parameter(self):
        # Test the for timezone correctness: dtstart should preserve it's
        # timezone, crated, dtstamp and last-modified must be in UTC.
        comp = Component()
        comp.add('X-TEST-PROP', 'tryout.',
                 parameters={'prop1': 'val1', 'prop2': 'val2'})
        lines = comp.to_ical().splitlines()
        self.assertTrue(b"X-TEST-PROP;PROP1=val1;PROP2=val2:tryout." in lines)

    def test_cal_Component_from_ical(self):
        # Check for proper handling of TZID parameter of datetime properties
        for component_name, property_name in (
            ('VEVENT', 'DTSTART'),
            ('VEVENT', 'DTEND'),
            ('VEVENT', 'RECURRENCE-ID'),
            ('VTODO', 'DUE')
        ):
            component_str = 'BEGIN:' + component_name + '\n'
            component_str += property_name + ';TZID=America/Denver:'
            component_str += '20120404T073000\nEND:' + component_name
            component = Component.from_ical(component_str)
            self.assertEqual(str(component[property_name].dt.tzinfo.zone),
                             "America/Denver")

            component_str = 'BEGIN:' + component_name + '\n'
            component_str += property_name + ':'
            component_str += '20120404T073000\nEND:' + component_name
            component = Component.from_ical(component_str)
            self.assertEqual(component[property_name].dt.tzinfo,
                             None)

    def test_cal_Component_to_ical_property_order(self):
        component_str = [b'BEGIN:VEVENT',
                         b'DTSTART:19970714T170000Z',
                         b'DTEND:19970715T035959Z',
                         b'SUMMARY:Bastille Day Party',
                         b'END:VEVENT']
        component = Component.from_ical(b'\r\n'.join(component_str))

        sorted_str = component.to_ical().splitlines()
        assert sorted_str != component_str
        assert set(sorted_str) == set(component_str)

        preserved_str = component.to_ical(sorted=False).splitlines()
        assert preserved_str == component_str

    def test_cal_Component_to_ical_parameter_order(self):
        component_str = [b'BEGIN:VEVENT',
                         b'X-FOOBAR;C=one;A=two;B=three:helloworld.',
                         b'END:VEVENT']
        component = Component.from_ical(b'\r\n'.join(component_str))

        sorted_str = component.to_ical().splitlines()
        assert sorted_str[0] == component_str[0]
        assert sorted_str[1] == b'X-FOOBAR;A=two;B=three;C=one:helloworld.'
        assert sorted_str[2] == component_str[2]

        preserved_str = component.to_ical(sorted=False).splitlines()
        assert preserved_str == component_str

    def test_repr(self):
        """Test correct class representation.
        """
        component = Component()
        component['key1'] = 'value1'

        self.assertTrue(
            re.match(r"Component\({u?'KEY1': u?'value1'}\)", str(component))
        )

        calendar = Calendar()
        calendar['key1'] = 'value1'

        self.assertTrue(
            re.match(r"VCALENDAR\({u?'KEY1': u?'value1'}\)", str(calendar))
        )

        event = Event()
        event['key1'] = 'value1'

        self.assertTrue(
            re.match(r"VEVENT\({u?'KEY1': u?'value1'}\)", str(event))
        )

        # Representation of nested Components
        nested = Component(key1='VALUE1')
        nested.add_component(component)
        calendar.add_component(event)
        nested.add_component(calendar)

        self.assertTrue(
            re.match(
                r"Component\({u?'KEY1': u?'VALUE1'}, "
                r"Component\({u?'KEY1': u?'value1'}\), "
                r"VCALENDAR\({u?'KEY1': u?'value1'}, "
                r"VEVENT\({u?'KEY1': u?'value1'}\)\)\)",
                str(nested)
            )
        )


def test_component_factory_VEVENT(factory):
    """Check the events in the component factory"""
    component = factory['VEVENT']
    event = component(dtstart='19700101')
    assert event.to_ical() == b'BEGIN:VEVENT\r\nDTSTART:19700101\r\nEND:VEVENT\r\n'


def test_component_factory_VCALENDAR(factory):
    """Check the VCALENDAR in the factory."""
    assert factory.get('VCALENDAR') == icalendar.cal.Calendar


def test_minimal_calendar_component_with_one_event():
    """Setting up a minimal calendar component looks like this"""
    cal = Calendar()

    # Some properties are required to be compliant
    cal['prodid'] = '-//My calendar product//mxm.dk//'
    cal['version'] = '2.0'

    # We also need at least one subcomponent for a calendar to be compliant
    event = Event()
    event['summary'] = 'Python meeting about calendaring'
    event['uid'] = '42'
    event.add('dtstart', datetime(2005, 4, 4, 8, 0, 0))
    cal.add_component(event)
    assert cal.subcomponents[0].to_ical() == \
        b'BEGIN:VEVENT\r\nSUMMARY:Python meeting about calendaring\r\n' \
        + b'DTSTART:20050404T080000\r\nUID:42\r\n' \
        + b'END:VEVENT\r\n'


def test_calendar_with_parsing_errors_includes_all_events(calendars):
    """Parsing a complete calendar from a string will silently ignore wrong
    events but adding the error information to the component's 'errors'
    attribute. The error in the following is the third EXDATE: it has an
    empty DATE.
    """
    event_descriptions = [e['DESCRIPTION'].to_ical() for e in calendars.parsing_error.walk('VEVENT')]
    assert event_descriptions == [b'Perfectly OK event', b'Wrong event']


def test_calendar_with_parsing_errors_has_an_error_in_one_event(calendars):
    """Parsing a complete calendar from a string will silently ignore wrong
    events but adding the error information to the component's 'errors'
    attribute. The error in the following is the third EXDATE: it has an
    empty DATE.
    """
    errors = [e.errors for e in calendars.parsing_error.walk('VEVENT')]
    assert errors == [[], [('EXDATE', "Expected datetime, date, or time, got: ''")]]


def test_cal_strict_parsing(calendars):
    """If components are damaged, we raise an exception."""
    with pytest.raises(ValueError):
        calendars.parsing_error_in_UTC_offset


def test_cal_ignore_errors_parsing(calendars, vUTCOffset_ignore_exceptions):
    """If we diable the errors, we should be able to put the calendar back together."""
    assert calendars.parsing_error_in_UTC_offset.to_ical() == calendars.parsing_error_in_UTC_offset.raw_ics



@pytest.mark.parametrize(
    'calendar, other_calendar',
    itertools.product([
        'issue_156_RDATE_with_PERIOD_TZID_khal',
        'issue_156_RDATE_with_PERIOD_TZID_khal_2',
        'issue_178_custom_component_contains_other',
        'issue_178_custom_component_inside_other',
        'issue_526_calendar_with_events',
        'issue_526_calendar_with_different_events',
        'issue_526_calendar_with_event_subset',
    ], repeat=2)
)
def test_comparing_calendars(calendars, calendar, other_calendar):
    are_calendars_equal = calendars[calendar] == calendars[other_calendar]
    are_calendars_actually_equal = calendar == other_calendar
    assert are_calendars_equal == are_calendars_actually_equal


@pytest.mark.parametrize('calendar, shuffeled_calendar', [
    (
        'issue_526_calendar_with_events',
        'issue_526_calendar_with_shuffeled_events',
    ),
])
def test_calendars_with_same_subcomponents_in_different_order_are_equal(calendars, calendar, shuffeled_calendar):
    assert not calendars[calendar].subcomponents == calendars[shuffeled_calendar].subcomponents
    assert calendars[calendar] == calendars[shuffeled_calendar]
