# -*- coding: utf-8 -*-
from datetime import datetime
from icalendar.parser_tools import to_unicode
from icalendar.prop import vDatetime
from icalendar.prop import vText
from string import ascii_letters
from string import digits

import random


class UIDGenerator(object):
    """If you are too lazy to create real uid's.

    """
    chars = list(ascii_letters + digits)

    def rnd_string(self, length=16):
        """Generates a string with random characters of length.
        """
        return ''.join([random.choice(self.chars) for _ in range(length)])

    def uid(self, host_name='example.com', unique=''):
        """Generates a unique id consisting of:
            datetime-uniquevalue@host.
        Like:
            20050105T225746Z-HKtJMqUgdO0jDUwm@example.com
        """
        host_name = to_unicode(host_name)
        unique = unique or self.rnd_string()
        today = to_unicode(vDatetime(datetime.today()).to_ical())
        return vText('%s-%s@%s' % (today,
                                   unique,
                                   host_name))
