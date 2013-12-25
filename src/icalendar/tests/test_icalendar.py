# coding: utf-8
from icalendar.tests import unittest


class IcalendarTestCase (unittest.TestCase):

    def test_long_lines(self):
        from ..parser import Contentlines, Contentline
        c = Contentlines([Contentline('BEGIN:VEVENT')])
        c.append(Contentline(''.join('123456789 ' * 10)))
        self.assertEqual(
            c.to_ical(),
            b'BEGIN:VEVENT\r\n123456789 123456789 123456789 123456789 '
            b'123456789 123456789 123456789 1234\r\n 56789 123456789 '
            b'123456789 \r\n'
        )

        # from doctests
        # Notice that there is an extra empty string in the end of the content
        # lines. That is so they can be easily joined with:
        # '\r\n'.join(contentlines))
        self.assertEqual(Contentlines.from_ical('A short line\r\n'),
                         ['A short line', ''])
        self.assertEqual(Contentlines.from_ical('A faked\r\n  long line\r\n'),
                         ['A faked long line', ''])
        self.assertEqual(
            Contentlines.from_ical('A faked\r\n  long line\r\nAnd another '
                                   'lin\r\n\te that is folded\r\n'),
            ['A faked long line', 'And another line that is folded', '']
        )

    def test_contentline_class(self):
        from ..parser import Contentline, Parameters
        from ..prop import vText

        self.assertEqual(
            Contentline('Si meliora dies, ut vina, poemata reddit').to_ical(),
            b'Si meliora dies, ut vina, poemata reddit'
        )

        # A long line gets folded
        c = Contentline(''.join(['123456789 '] * 10)).to_ical()
        self.assertEqual(
            c,
            (b'123456789 123456789 123456789 123456789 123456789 123456789 '
             b'123456789 1234\r\n 56789 123456789 123456789 ')
        )

        # A folded line gets unfolded
        self.assertEqual(
            Contentline.from_ical(c),
            ('123456789 123456789 123456789 123456789 123456789 123456789 '
             '123456789 123456789 123456789 123456789 ')
        )

        # http://tools.ietf.org/html/rfc5545#section-3.3.11
        # An intentional formatted text line break MUST only be included in
        # a "TEXT" property value by representing the line break with the
        # character sequence of BACKSLASH, followed by a LATIN SMALL LETTER
        # N or a LATIN CAPITAL LETTER N, that is "\n" or "\N".

        # Newlines are not allwoed in content lines
        self.assertRaises(AssertionError, Contentline, b'1234\r\n\r\n1234')

        self.assertEqual(
            Contentline('1234\\n\\n1234').to_ical(),
            b'1234\\n\\n1234'
        )

        # We do not fold within a UTF-8 character
        c = Contentline(b'This line has a UTF-8 character where it should be '
                        b'folded. Make sure it g\xc3\xabts folded before that '
                        b'character.')

        self.assertIn(b'\xc3\xab', c.to_ical())

        # Another test of the above
        c = Contentline(b'x' * 73 + b'\xc3\xab' + b'\\n ' + b'y' * 10)

        self.assertEqual(c.to_ical().count(b'\xc3'), 1)

        # Don't fail if we fold a line that is exactly X times 74 characters
        # long
        c = Contentline(''.join(['x'] * 148)).to_ical()

        # It can parse itself into parts,
        # which is a tuple of (name, params, vals)
        self.assertEqual(
            Contentline('dtstart:20050101T120000').parts(),
            ('dtstart', Parameters({}), '20050101T120000')
        )

        self.assertEqual(
            Contentline('dtstart;value=datetime:20050101T120000').parts(),
            ('dtstart', Parameters({'VALUE': 'datetime'}), '20050101T120000')
        )

        c = Contentline('ATTENDEE;CN=Max Rasmussen;ROLE=REQ-PARTICIPANT:'
                        'MAILTO:maxm@example.com')
        self.assertEqual(
            c.parts(),
            ('ATTENDEE',
             Parameters({'ROLE': 'REQ-PARTICIPANT', 'CN': 'Max Rasmussen'}),
             'MAILTO:maxm@example.com')
        )
        self.assertEqual(
            c.to_ical().decode('utf-8'),
            'ATTENDEE;CN=Max Rasmussen;ROLE=REQ-PARTICIPANT:'
            'MAILTO:maxm@example.com'
        )

        # and back again
        # NOTE: we are quoting property values with spaces in it.
        parts = ('ATTENDEE',
                 Parameters({'ROLE': 'REQ-PARTICIPANT',
                             'CN': 'Max Rasmussen'}),
                 'MAILTO:maxm@example.com')
        self.assertEqual(
            Contentline.from_parts(*parts),
            'ATTENDEE;CN="Max Rasmussen";ROLE=REQ-PARTICIPANT:'
            'MAILTO:maxm@example.com'
        )

        # and again
        parts = ('ATTENDEE', Parameters(), 'MAILTO:maxm@example.com')
        self.assertEqual(
            Contentline.from_parts(*parts),
            'ATTENDEE:MAILTO:maxm@example.com'
        )

        # A value can also be any of the types defined in PropertyValues
        parts = ('ATTENDEE', Parameters(), vText('MAILTO:test@example.com'))
        self.assertEqual(
            Contentline.from_parts(*parts),
            'ATTENDEE:MAILTO:test@example.com'
        )

        # A value in UTF-8
        parts = ('SUMMARY', Parameters(), vText('INternational char æ ø å'))
        self.assertEqual(
            Contentline.from_parts(*parts),
            u'SUMMARY:INternational char æ ø å'
        )

        # A value can also be unicode
        parts = ('SUMMARY', Parameters(), vText(u'INternational char æ ø å'))
        self.assertEqual(
            Contentline.from_parts(*parts),
            u'SUMMARY:INternational char æ ø å'
        )

        # Traversing could look like this.
        name, params, vals = c.parts()
        self.assertEqual(name, 'ATTENDEE')
        self.assertEqual(vals, 'MAILTO:maxm@example.com')
        self.assertEqual(
            sorted(params.items()),
            sorted([('ROLE', 'REQ-PARTICIPANT'), ('CN', 'Max Rasmussen')])
        )

        # And the traditional failure
        with self.assertRaisesRegexp(
            ValueError,
            'Content line could not be parsed into parts'
        ):
            Contentline('ATTENDEE;maxm@example.com').parts()

        # Another failure:
        with self.assertRaisesRegexp(
            ValueError,
            'Content line could not be parsed into parts'
        ):
            Contentline(':maxm@example.com').parts()

        self.assertEqual(
            Contentline('key;param=:value').parts(),
            ('key', Parameters({'PARAM': ''}), 'value')
        )

        self.assertEqual(
            Contentline('key;param="pvalue":value').parts(),
            ('key', Parameters({'PARAM': 'pvalue'}), 'value')
        )

        # Should bomb on missing param:
        with self.assertRaisesRegexp(
            ValueError,
            'Content line could not be parsed into parts'
        ):
            Contentline.from_ical("k;:no param").parts()

        self.assertEqual(
            Contentline('key;param=pvalue:value', strict=False).parts(),
            ('key', Parameters({'PARAM': 'pvalue'}), 'value')
        )

        # If strict is set to True, uppercase param values that are not
        # double-quoted, this is because the spec says non-quoted params are
        # case-insensitive.
        self.assertEqual(
            Contentline('key;param=pvalue:value', strict=True).parts(),
            ('key', Parameters({'PARAM': 'PVALUE'}), 'value')
        )

        self.assertEqual(
            Contentline('key;param="pValue":value', strict=True).parts(),
            ('key', Parameters({'PARAM': 'pValue'}), 'value')
        )

    def test_fold_line(self):
        from ..parser import foldline

        self.assertEqual(foldline(u'foo'), u'foo')
        self.assertEqual(
            foldline(u"Lorem ipsum dolor sit amet, consectetur adipiscing "
                     u"elit. Vestibulum convallis imperdiet dui posuere."),
            (u'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '
             u'Vestibulum conval\r\n lis imperdiet dui posuere.')
        )

        # I don't really get this test
        # at least just but bytes in there
        # porting it to "run" under python 2 & 3 makes it not much better
        with self.assertRaises(AssertionError):
            foldline(u'привет'.encode('utf-8'), limit=3)

        self.assertEqual(foldline(u'foobar', limit=4), u'foo\r\n bar')
        self.assertEqual(
            foldline(u'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
                     u'. Vestibulum convallis imperdiet dui posuere.'),
            (u'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
             u' Vestibulum conval\r\n lis imperdiet dui posuere.')
        )
        self.assertEqual(
            foldline(u'DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ'),
            u'DESCRIPTION:АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭ\r\n ЮЯ'
        )

    def test_value_double_quoting(self):
        from ..parser import dquote
        self.assertEqual(dquote('Max'), 'Max')
        self.assertEqual(dquote('Rasmussen, Max'), '"Rasmussen, Max"')
        self.assertEqual(dquote('name:value'), '"name:value"')

    def test_q_split(self):
        from ..parser import q_split
        self.assertEqual(q_split('Max,Moller,"Rasmussen, Max"'),
                         ['Max', 'Moller', '"Rasmussen, Max"'])

    def test_q_join(self):
        from ..parser import q_join
        self.assertEqual(q_join(['Max', 'Moller', 'Rasmussen, Max']),
                         'Max,Moller,"Rasmussen, Max"')
