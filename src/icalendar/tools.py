from __future__ import absolute_import
import random
from string import (
    ascii_letters,
    digits,
)
from datetime import datetime
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
        unique = unique or self.rnd_string()
        return vText('%s-%s@%s' % (vDatetime(datetime.today()).to_ical(),
                                   unique,
                                   host_name))
