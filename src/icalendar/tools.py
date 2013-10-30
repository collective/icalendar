from __future__ import absolute_import
import random
from string import (
    ascii_letters,
    digits,
)
from datetime import datetime
from .parser_tools import to_unicode
from .prop import (
    vText,
    vDatetime,
)


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
