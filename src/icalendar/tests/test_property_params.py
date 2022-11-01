import pytest
from icalendar import Calendar, Event, Parameters, vCalAddress

import unittest
import icalendar
import re

@pytest.mark.parametrize('parameter, expected', [
    # Simple parameter:value pair
    (Parameters(parameter1='Value1'), b'PARAMETER1=Value1'),
    # Parameter with list of values must be separated by comma
    (Parameters({'parameter1': ['Value1', 'Value2']}), b'PARAMETER1=Value1,Value2'),
    # Multiple parameters must be separated by a semicolon
    (Parameters({'RSVP': 'TRUE', 'ROLE': 'REQ-PARTICIPANT'}), b'ROLE=REQ-PARTICIPANT;RSVP=TRUE'),
    # Parameter values containing ',;:' must be double quoted
    (Parameters({'ALTREP': 'http://www.wiz.org'}), b'ALTREP="http://www.wiz.org"'),
    # list items must be quoted separately
    (Parameters({'MEMBER': ['MAILTO:projectA@host.com',
                                   'MAILTO:projectB@host.com']}),
     b'MEMBER="MAILTO:projectA@host.com","MAILTO:projectB@host.com"'),
    (Parameters({'parameter1': 'Value1',
                        'parameter2': ['Value2', 'Value3'],
                        'ALTREP': ['http://www.wiz.org', 'value4']}),
     b'ALTREP="http://www.wiz.org",value4;PARAMETER1=Value1;PARAMETER2=Value2,Value3'),
    # Including empty strings
    (Parameters({'PARAM': ''}), b'PARAM='),
    # We can also parse parameter strings
    (Parameters({'MEMBER': ['MAILTO:projectA@host.com',
                                   'MAILTO:projectB@host.com']}),
     b'MEMBER="MAILTO:projectA@host.com","MAILTO:projectB@host.com"'),
    # We can also parse parameter strings
    (Parameters({'PARAMETER1': 'Value1',
                 'ALTREP': ['http://www.wiz.org', 'value4'],
                 'PARAMETER2': ['Value2', 'Value3']}),
     b'ALTREP="http://www.wiz.org",value4;PARAMETER1=Value1;PARAMETER2=Value2,Value3'),
])
def test_parameter_to_ical_is_inverse_of_from_ical(parameter, expected):
    assert parameter.to_ical() == expected
    assert Parameters.from_ical(expected.decode('utf-8')) == parameter

def test_parse_parameter_string_without_quotes():
    assert Parameters.from_ical('PARAM1=Value 1;PARA2=Value 2') == Parameters({'PARAM1': 'Value 1', 'PARA2': 'Value 2'})

def test_parametr_is_case_insensitive():
    parameter = Parameters(parameter1='Value1')
    assert parameter['parameter1'] == parameter['PARAMETER1'] == parameter['PaRaMeTer1']

def test_parameter_keys_are_uppercase():
    parameter = Parameters(parameter1='Value1')
    assert list(parameter.keys()) == ['PARAMETER1']

@pytest.mark.parametrize('cn_param, cn_quoted', [
    # not double-quoted
    ('Aramis', 'Aramis'),
    # if a space is present - enclose in double quotes
    ('Aramis Alameda', '"Aramis Alameda"'),
    # a single quote in parameter value - double quote the value
    ('Aramis d\'Alameda', '"Aramis d\'Alameda"'),
    ('Арамис д\'Аламеда', '"Арамис д\'Аламеда"'),
    # double quote is replaced with single quote
    ('Aramis d\"Alameda', '"Aramis d\'Alameda"'),
])
def test_quoting(cn_param, cn_quoted):
    event = Event()
    attendee = vCalAddress('test@example.com')
    attendee.params['CN'] = cn_param
    event.add('ATTENDEE', attendee)
    assert f'ATTENDEE;CN={cn_quoted}:test@example.com' in event.to_ical().decode('utf-8')

class TestPropertyParams(unittest.TestCase):

    def test_property_params(self):
        # Property parameters with values containing a COLON character, a
        # SEMICOLON character or a COMMA character MUST be placed in quoted
        # text.
        cal_address = vCalAddress('mailto:john.doe@example.org')
        cal_address.params["CN"] = "Doe, John"
        ical = Calendar()
        ical.add('organizer', cal_address)

        ical_str = Calendar.to_ical(ical)
        exp_str = b"""BEGIN:VCALENDAR\r\nORGANIZER;CN="Doe, John":"""\
                  b"""mailto:john.doe@example.org\r\nEND:VCALENDAR\r\n"""

        self.assertEqual(ical_str, exp_str)

        # other way around: ensure the property parameters can be restored from
        # an icalendar string.
        ical2 = Calendar.from_ical(ical_str)
        self.assertEqual(ical2.get('ORGANIZER').params.get('CN'), 'Doe, John')

    def test_parse_and_access_property_params(self):
        """Parse an ics string and access some property parameters then.
        This is a follow-up of a question received per email.

        """
        ics = """BEGIN:VCALENDAR
VERSION:2.0
PRODID://RESEARCH IN MOTION//BIS 3.0
METHOD:REQUEST
BEGIN:VEVENT
SEQUENCE:2
X-RIM-REVISION:0
SUMMARY:Test meeting from BB
X-MICROSOFT-CDO-ALLDAYEVENT:TRUE
CLASS:PUBLIC
ATTENDEE;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN="RembrandXS":MAILTO:rembrand@xs4all.nl
ATTENDEE;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN="RembrandDX":MAILTO:rembrand@daxlab.com
ATTENDEE;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN="RembrandSB":MAILTO:rembspam@xs4all.nl
UID:XRIMCAL-628059586-522954492-9750559
DTSTART;VALUE=DATE:20120814
DTEND;VALUE=DATE:20120815
DESCRIPTION:Test meeting from BB
DTSTAMP:20120813T151458Z
ORGANIZER:mailto:rembrand@daxlab.com
END:VEVENT
END:VCALENDAR"""

        cal = icalendar.Calendar.from_ical(ics)
        event = cal.walk("VEVENT")[0]
        event['attendee'][0]
        self.assertEqual(event['attendee'][0].to_ical(),
                         b'MAILTO:rembrand@xs4all.nl')
        self.assertEqual(event['attendee'][0].params.to_ical(),
                         b'CN=RembrandXS;PARTSTAT=NEEDS-ACTION;RSVP=TRUE')
        self.assertEqual(event['attendee'][0].params['cn'], 'RembrandXS')

    def test_repr(self):
        """Test correct class representation.
        """
        it = Parameters(parameter1='Value1')
        self.assertTrue(
            re.match(r"Parameters\({u?'PARAMETER1': u?'Value1'}\)", str(it))
        )
