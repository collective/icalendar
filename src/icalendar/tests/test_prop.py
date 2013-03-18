from datetime import datetime, date, timedelta
import unittest

import icalendar
import pytz


class TestProp(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestProp, self).__init__(*args, **kwargs)
        self.at = self.assertTrue

    def test_prop_vBinary(self):
        vBinary = icalendar.prop.vBinary

        txt = 'This is gibberish'
        txt_ical = 'VGhpcyBpcyBnaWJiZXJpc2g='
        self.assertTrue(vBinary(txt).to_ical() == txt_ical)
        self.assertTrue(vBinary.from_ical(txt_ical) == txt)

        # The roundtrip test
        txt = 'Binary data \x13 \x56'
        txt_ical = 'QmluYXJ5IGRhdGEgEyBW'
        self.assertTrue(vBinary(txt).to_ical() == txt_ical)
        self.assertTrue(vBinary.from_ical(txt_ical) == txt)

        self.assertTrue(str(vBinary('txt').params) ==\
            "Parameters({'VALUE': 'BINARY', 'ENCODING': 'BASE64'})")

        # Long data should not have line breaks, as that would interfere
        txt = 'a'*99
        txt_ical = 'YWFh'*33
        self.assertTrue(vBinary(txt).to_ical() == txt_ical)
        self.assertTrue(vBinary.from_ical(txt_ical) == txt)


    def test_prop_vBoolean(self):
        vBoolean = icalendar.prop.vBoolean

        self.assertTrue(vBoolean(True).to_ical() == 'TRUE')
        self.assertTrue(vBoolean(0).to_ical() == 'FALSE')

        # The roundtrip test
        self.assertTrue(vBoolean.from_ical(vBoolean(True).to_ical()) == True)
        self.assertTrue(vBoolean.from_ical('true') == True)


    def test_prop_vCalAddress(self):
        vCalAddress = icalendar.prop.vCalAddress
        txt = 'MAILTO:maxm@mxm.dk'
        a = vCalAddress(txt)
        a.params['cn'] = 'Max M'

        self.assertTrue(a.to_ical() == txt)
        self.assertTrue(str(a.params) == "Parameters({'CN': 'Max M'})")
        self.assertTrue(vCalAddress.from_ical(txt) == 'MAILTO:maxm@mxm.dk')


    def test_prop_vFloat(self):
        vFloat = icalendar.prop.vFloat
        self.assertTrue(vFloat(1.0).to_ical() == '1.0')
        self.assertTrue(vFloat.from_ical('42') == 42.0)
        self.assertTrue(vFloat(42).to_ical() == '42.0')


    def test_prop_vInt(self):
        vInt = icalendar.prop.vInt
        self.assertTrue(vInt(42).to_ical() == '42')
        self.assertTrue(vInt.from_ical('13') == 13)
        self.assertRaises(ValueError, vInt.from_ical, '1s3')


    def test_prop_vDDDLists(self):
        vDDDLists = icalendar.prop.vDDDLists

        dt_list = vDDDLists.from_ical('19960402T010000Z')
        self.assertTrue(type(dt_list) == list)
        self.assertTrue(len(dt_list) == 1)
        self.assertTrue(type(dt_list[0]) == datetime)
        self.assertTrue(str(dt_list[0]) == '1996-04-02 01:00:00+00:00')

        p = '19960402T010000Z,19960403T010000Z,19960404T010000Z'
        dt_list = vDDDLists.from_ical(p)
        self.assertTrue(len(dt_list) == 3)
        self.assertTrue(str(dt_list[0]) == '1996-04-02 01:00:00+00:00')
        self.assertTrue(str(dt_list[2]) == '1996-04-04 01:00:00+00:00')

        dt_list = vDDDLists([])
        self.assertTrue(dt_list.to_ical() == '')

        dt_list = vDDDLists([datetime(2000,1,1)])
        self.assertTrue(dt_list.to_ical() == '20000101T000000')

        dt_list = vDDDLists([datetime(2000,1,1), datetime(2000,11,11)])
        self.assertTrue(dt_list.to_ical() == '20000101T000000,20001111T000000')


    def test_prop_vDDDTypes(self):
        vDDDTypes = icalendar.prop.vDDDTypes

        self.assertTrue(type(vDDDTypes.from_ical('20010101T123000')) ==
                        datetime)

        self.assertTrue(vDDDTypes.from_ical('20010101T123000Z') ==
                        datetime(2001, 1, 1, 12, 30, tzinfo=pytz.utc))

        self.assertTrue(type(vDDDTypes.from_ical('20010101')) == date)

        self.assertTrue(vDDDTypes.from_ical('P31D') == timedelta(31))

        self.assertTrue(vDDDTypes.from_ical('-P31D') == timedelta(-31))

        # Bad input
        self.assertRaises(ValueError, vDDDTypes, 42)


    def test_prop_vDate(self):
        vDate = icalendar.prop.vDate

        self.assertTrue(vDate(date(2001, 1, 1)).to_ical() == '20010101')
        self.assertTrue(vDate(date(1899, 1, 1)).to_ical() == '18990101')

        self.assertTrue(vDate.from_ical('20010102') == date(2001, 1, 2))

        self.assertRaises(ValueError, vDate, 'd')


    def test_prop_vDatetime(self):
        vDatetime = icalendar.prop.vDatetime

        dt = datetime(2001, 1, 1, 12, 30, 0)
        self.assertTrue(vDatetime(dt).to_ical() == '20010101T123000')

        self.assertTrue(vDatetime.from_ical('20000101T120000') ==
                        datetime(2000, 1, 1, 12, 0))

        dutc = datetime(2001, 1,1, 12, 30, 0, tzinfo=pytz.utc)
        self.assertTrue(vDatetime(dutc).to_ical() == '20010101T123000Z')

        dutc = datetime(1899, 1,1, 12, 30, 0, tzinfo=pytz.utc)
        self.assertTrue(vDatetime(dutc).to_ical() == '18990101T123000Z')

        self.assertTrue(vDatetime.from_ical('20010101T000000') ==
                        datetime(2001, 1, 1, 0, 0))

        self.assertRaises(ValueError, vDatetime.from_ical, '20010101T000000A')

        utc = vDatetime.from_ical('20010101T000000Z')
        self.assertTrue(vDatetime(utc).to_ical() == '20010101T000000Z')

        # 1 minute before transition to DST
        dat = vDatetime.from_ical('20120311T015959', 'America/Denver')
        self.assertTrue(dat.strftime('%Y%m%d%H%M%S %z') ==
                        '20120311015959 -0700')

        # After transition to DST
        dat = vDatetime.from_ical('20120311T030000', 'America/Denver')
        self.assertTrue(dat.strftime('%Y%m%d%H%M%S %z') ==
                        '20120311030000 -0600')

        dat = vDatetime.from_ical('20101010T000000', 'Europe/Vienna')
        self.assertTrue(vDatetime(dat).to_ical() == '20101010T000000')


    def test_prop_vDuration(self):
        vDuration = icalendar.prop.vDuration

        self.at(vDuration(timedelta(11)).to_ical() == 'P11D')
        self.at(vDuration(timedelta(-14)).to_ical() == '-P14D')
        self.at(vDuration(timedelta(1, 7384)).to_ical() == 'P1DT2H3M4S')
        self.at(vDuration(timedelta(1, 7380)).to_ical() == 'P1DT2H3M')
        self.at(vDuration(timedelta(1, 7200)).to_ical() == 'P1DT2H')
        self.at(vDuration(timedelta(0, 7200)).to_ical() == 'PT2H')
        self.at(vDuration(timedelta(0, 7384)).to_ical() == 'PT2H3M4S')
        self.at(vDuration(timedelta(0, 184)).to_ical() == 'PT3M4S')
        self.at(vDuration(timedelta(0, 22)).to_ical() == 'PT22S')
        self.at(vDuration(timedelta(0, 3622)).to_ical() == 'PT1H0M22S')
        self.at(vDuration(timedelta(days=1, hours=5)).to_ical() == 'P1DT5H')
        self.at(vDuration(timedelta(hours=-5)).to_ical() == '-PT5H')
        self.at(vDuration(timedelta(days=-1, hours=-5)).to_ical() == '-P1DT5H')

        # How does the parsing work?
        self.at(vDuration.from_ical('PT1H0M22S') == timedelta(0, 3622))

        self.assertRaises(ValueError, vDuration.from_ical, 'kox')

        self.at(vDuration.from_ical('-P14D') == timedelta(-14))

        self.assertRaises(ValueError, vDuration, 11)













class TestPropertyValues(unittest.TestCase):

    def test_vDDDLists_timezone(self):
        """Test vDDDLists with timezone information.
        """
        e = icalendar.Event()
        at = pytz.timezone('Europe/Vienna')
        dt1 = at.localize(datetime(2013, 1, 1))
        dt2 = at.localize(datetime(2013, 1, 2))
        dt3 = at.localize(datetime(2013, 1, 3))
        e.add('rdate', [dt1, dt2])
        e.add('exdate', dt3)
        out = e.to_ical()

        self.assertTrue('RDATE;TZID=Europe/Vienna:20130101T000000,20130102T000000' in out)
        self.assertTrue('EXDATE;TZID=Europe/Vienna:20130103T000000' in out)

        # 'BEGIN:VEVENT\r\nDTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130101T000000\r\nRDATE;TZID=Europe/Vienna:20130101T000000,20130102T000000\r\nEXDATE;TZID=Europe/Vienna:20130103T000000\r\nEND:VEVENT\r\n'
