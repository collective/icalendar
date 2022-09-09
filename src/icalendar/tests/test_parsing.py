'''Tests checking that parsing works'''
import pytest

from icalendar.parser import Contentline, Parameters

@pytest.mark.parametrize('raw_content_line, expected_output', [
    # Issue #142 - Multivalued parameters. This is needed for VCard 3.0.
    # see https://github.com/collective/icalendar/pull/142
    ('TEL;TYPE=HOME,VOICE:000000000', ('TEL', Parameters({'TYPE': ['HOME', 'VOICE']}), '000000000')),
    # Issue #143 - Allow dots in property names. Another vCard related issue.
    # see https://github.com/collective/icalendar/pull/143
    ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR:;;This is the Adress 08; Some City;;12345;Germany', \
        ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.ADR', \
        Parameters(),\
        ';;This is the Adress 08; Some City;;12345;Germany')),
    ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.X-ABLABEL:', \
        ('ITEMADRNULLTHISISTHEADRESS08158SOMECITY12345.X-ABLABEL', \
        Parameters(), \
        ''))
])
def test_content_lines_parsed_properly(raw_content_line, expected_output):
    assert Contentline.from_ical(raw_content_line).parts() == expected_output

