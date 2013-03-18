from datetime import datetime, date, timedelta, time
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


    def test_prop_vPeriod(self):
        vPeriod = icalendar.prop.vPeriod

        # One day in exact datetimes
        per = (datetime(2000,1,1), datetime(2000,1,2))
        self.at(vPeriod(per).to_ical() == '20000101T000000/20000102T000000')

        per = (datetime(2000,1,1), timedelta(days=31))
        self.at(vPeriod(per).to_ical() == '20000101T000000/P31D')

        # Roundtrip
        p = vPeriod.from_ical('20000101T000000/20000102T000000')
        self.at(p == (datetime(2000, 1, 1, 0, 0), datetime(2000, 1, 2, 0, 0)))
        self.at(vPeriod(p).to_ical() == '20000101T000000/20000102T000000')

        self.at(vPeriod.from_ical('20000101T000000/P31D') ==
                (datetime(2000, 1, 1, 0, 0), timedelta(31)))

        # Roundtrip with absolute time
        p = vPeriod.from_ical('20000101T000000Z/20000102T000000Z')
        self.at(vPeriod(p).to_ical() == '20000101T000000Z/20000102T000000Z')

        # And an error
        self.assertRaises(ValueError,
                          vPeriod.from_ical, '20000101T000000/Psd31D')

        # Timezoned
        dk = pytz.timezone('Europe/Copenhagen')
        start = datetime(2000,1,1, tzinfo=dk)
        end = datetime(2000,1,2, tzinfo=dk)
        per = (start, end)
        self.at(vPeriod(per).to_ical() == '20000101T000000/20000102T000000')
        self.at(vPeriod(per).params['TZID'] == 'Europe/Copenhagen')

        p = vPeriod((datetime(2000,1,1, tzinfo=dk), timedelta(days=31)))
        self.at(p.to_ical() == '20000101T000000/P31D')


    def test_prop_vWeekday(self):
        vWeekday = icalendar.prop.vWeekday

        self.at(vWeekday('mo').to_ical() == 'MO')
        self.assertRaises(ValueError, vWeekday, 'erwer')
        self.at(vWeekday.from_ical('mo') == 'MO')
        self.at(vWeekday.from_ical('+3mo') == '+3MO')
        self.assertRaises(ValueError, vWeekday.from_ical, 'Saturday')
        self.at(vWeekday('+mo').to_ical() == '+MO')
        self.at(vWeekday('+3mo').to_ical() == '+3MO')
        self.at(vWeekday('-tu').to_ical() == '-TU')


    def test_prop_vFrequency(self):
        vFrequency = icalendar.prop.vFrequency

        self.assertRaises(ValueError, vFrequency, 'bad test')
        self.at(vFrequency('daily').to_ical() == 'DAILY')
        self.at(vFrequency('daily').from_ical('MONTHLY') == 'MONTHLY')


    def test_prop_vRecur(self):
        vRecur = icalendar.prop.vRecur

        #Let's see how close we can get to one from the rfc:
        #FREQ=YEARLY;INTERVAL=2;BYMONTH=1;BYDAY=SU;BYHOUR=8,9;BYMINUTE=30

        r = dict(freq='yearly', interval=2)
        r['bymonth'] = 1
        r['byday'] = 'su'
        r['byhour'] = [8,9]
        r['byminute'] = 30
        self.at(vRecur(r).to_ical() ==
            'FREQ=YEARLY;INTERVAL=2;BYMINUTE=30;BYHOUR=8,9;BYDAY=SU;BYMONTH=1')

        r = vRecur(FREQ='yearly', INTERVAL=2)
        r['BYMONTH'] = 1
        r['BYDAY'] = 'su'
        r['BYHOUR'] = [8,9]
        r['BYMINUTE'] = 30
        self.at(r.to_ical() ==
            'FREQ=YEARLY;INTERVAL=2;BYMINUTE=30;BYHOUR=8,9;BYDAY=SU;BYMONTH=1')

        r = vRecur(freq='DAILY', count=10)
        r['bysecond'] = [0, 15, 30, 45]
        self.at(r.to_ical() == 'FREQ=DAILY;COUNT=10;BYSECOND=0,15,30,45')

        r = vRecur(freq='DAILY', until=datetime(2005,1,1,12,0,0))
        self.at(r.to_ical() == 'FREQ=DAILY;UNTIL=20050101T120000')

        # How do we fare with regards to parsing?
        r = vRecur.from_ical('FREQ=DAILY;INTERVAL=2;COUNT=10')
        self.at(r == {'COUNT': [10], 'FREQ': ['DAILY'], 'INTERVAL': [2]})
        self.at(vRecur(r).to_ical() == 'FREQ=DAILY;COUNT=10;INTERVAL=2')

        p = 'FREQ=YEARLY;INTERVAL=2;BYMONTH=1;BYDAY=-SU;BYHOUR=8,9;BYMINUTE=30'
        r = vRecur.from_ical(p)
        self.at(r == {'BYHOUR': [8, 9], 'BYDAY': ['-SU'], 'BYMINUTE': [30],
                     'BYMONTH': [1], 'FREQ': ['YEARLY'], 'INTERVAL': [2]})

        self.at(vRecur(r).to_ical() ==
          'FREQ=YEARLY;INTERVAL=2;BYMINUTE=30;BYHOUR=8,9;BYDAY=-SU;BYMONTH=1')

        # Some examples from the spec
        r = vRecur.from_ical('FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1')
        self.at(vRecur(r).to_ical() ==
                'FREQ=MONTHLY;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1')

        p = 'FREQ=YEARLY;INTERVAL=2;BYMONTH=1;BYDAY=SU;BYHOUR=8,9;BYMINUTE=30'
        r = vRecur.from_ical(p)
        self.at(vRecur(r).to_ical() ==
            'FREQ=YEARLY;INTERVAL=2;BYMINUTE=30;BYHOUR=8,9;BYDAY=SU;BYMONTH=1')

        # and some errors
        self.assertRaises(ValueError, vRecur.from_ical, 'BYDAY=12')


    def test_prop_vText(self):
        vText = icalendar.prop.vText

        self.at(vText(u'Simple text').to_ical() == 'Simple text')

        # Escaped text
        t = vText('Text ; with escaped, chars')
        self.at(t.to_ical() == 'Text \\; with escaped\\, chars')

        # Escaped newlines
        self.at(vText('Text with escaped\N chars').to_ical() ==
                'Text with escaped\\n chars')

        # If you pass a unicode object, it will be utf-8 encoded. As this is
        # the (only) standard that RFC 2445 support.
        t = vText(u'international chars \xe4\xf6\xfc')
        self.at(t.to_ical() ==
                'international chars \xc3\xa4\xc3\xb6\xc3\xbc')

        # and parsing?
        self.at(vText.from_ical('Text \\; with escaped\\, chars') ==
                u'Text ; with escaped, chars')

        t = vText.from_ical('A string with\\; some\\\\ characters in\\it')
        self.at(t == "A string with; some\\ characters in\it")

        # We are forgiving to utf-8 encoding errors:
        # We intentionally use a string with unexpected encoding
        self.at(vText.from_ical('Ol\xe9') == u'Ol\ufffd')

        # Notice how accented E character, encoded with latin-1, got replaced
        # with the official U+FFFD REPLACEMENT CHARACTER.


    def test_prop_vTime(self):
        vTime = icalendar.prop.vTime

        self.at(vTime(12, 30, 0).to_ical() == '123000')
        self.at(vTime.from_ical('123000') == time(12, 30))

        # We should also fail, right?
        self.assertRaises(ValueError, vTime.from_ical, '263000')


    def test_prop_vUri(self):
        vUri = icalendar.prop.vUri

        self.at(vUri('http://www.example.com/').to_ical() ==
                'http://www.example.com/')
        self.at(vUri.from_ical('http://www.example.com/') ==
                'http://www.example.com/')


    def test_prop_vGeo(self):
        vGeo = icalendar.prop.vGeo

        # Pass a list
        self.at(vGeo([1.2, 3.0]).to_ical() == '1.2;3.0')

        # Pass a tuple
        self.at(vGeo((1.2, 3.0)).to_ical() == '1.2;3.0')

        g = vGeo.from_ical('37.386013;-122.082932')
        self.at(g == (float('37.386013'), float('-122.082932')))

        self.at(vGeo(g).to_ical() == '37.386013;-122.082932')

        self.assertRaises(ValueError, vGeo, 'g')


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
