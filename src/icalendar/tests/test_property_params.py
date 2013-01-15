# coding: utf-8

import icalendar
import unittest


class TestPropertyParams(unittest.TestCase):

    def test_property_params(self):
        cal_address = icalendar.vCalAddress('mailto:john.doe@example.org')
        cal_address.params["CN"] = "Doe, John"
        ical = icalendar.Calendar()
        ical.add('organizer', cal_address)

        ical_str = icalendar.Calendar.to_ical(ical)
        exp_str = """BEGIN:VCALENDAR\r\nORGANIZER;CN="Doe, John":"""\
                  """mailto:john.doe@example.org\r\nEND:VCALENDAR\r\n"""

        self.assertEqual(ical_str, exp_str)

        # other way around: ensure the property parameters can be restored from
        # an icalendar string.
        ical2 = icalendar.Calendar.from_ical(ical_str)
        self.assertEqual(ical2.get('ORGANIZER').params.get('CN'), 'Doe, John')

    def test_quoting(self):
        # not double-quoted
        self._test_quoting(u"Aramis", 'Aramis')
        # if a space is present - enclose in double quotes
        self._test_quoting(u"Aramis Alameda", '"Aramis Alameda"')
        # a single quote in parameter value - double quote the value
        self._test_quoting("Aramis d'Alameda", '"Aramis d\'Alameda"')
        # double quote is replaced with single quote
        self._test_quoting("Aramis d\"Alameda", '"Aramis d\'Alameda"')
        self._test_quoting(u"Арамис д'Аламеда", '"Арамис д\'Аламеда"')

    def _test_quoting(self, cn_param, cn_quoted):
        """
        @param cn_param: CN parameter value to test for quoting
        @param cn_quoted: expected quoted parameter in icalendar format
        """
        vevent = icalendar.Event()
        attendee = icalendar.vCalAddress('test@mail.com')
        attendee.params['CN'] = cn_param
        vevent.add('ATTENDEE', attendee)
        self.assertEqual(
            vevent.to_ical(),
            'BEGIN:VEVENT\r\nATTENDEE;CN=%s:test@mail.com\r\nEND:VEVENT\r\n'
            % cn_quoted
        )
