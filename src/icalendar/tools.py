# Copyright (c) 2012, Plone Foundation
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""" This module contains non-essential tools for iCalendar. Pretty thin so far
eh?
"""

import random
from string import ascii_letters, digits
from datetime import datetime

class UIDGenerator:

    """
    If you are too lazy to create real uid's. Notice, this doctest is disabled!

    Automatic semi-random uid
    >> g = UIDGenerator()
    >> uid = g.uid()
    >> uid.to_ical()
    '20050109T153222-7ekDDHKcw46QlwZK@example.com'

    You should at least insert your own hostname to be more compliant
    >> g = UIDGenerator()
    >> uid = g.uid('Example.ORG')
    >> uid.to_ical()
    '20050109T153549-NbUItOPDjQj8Ux6q@Example.ORG'

    You can also insert a path or similar
    >> g = UIDGenerator()
    >> uid = g.uid('Example.ORG', '/path/to/content')
    >> uid.to_ical()
    '20050109T153415-/path/to/content@Example.ORG'
    """

    chars = list(ascii_letters + digits)

    def rnd_string(self, length=16):
        "Generates a string with random characters of length"
        return ''.join([random.choice(self.chars) for i in range(length)])

    def uid(self, host_name='example.com', unique=''):
        """
        Generates a unique id consisting of:
        datetime-uniquevalue@host. Like:
        20050105T225746Z-HKtJMqUgdO0jDUwm@example.com
        """
        from icalendar.prop import vText, vDatetime
        unique = unique or self.rnd_string()
        return vText('%s-%s@%s' % (vDatetime(datetime.today()).to_ical(), unique, host_name))


if __name__ == "__main__":
    import doctest, tools
    # import and test this file
    doctest.testmod(tools)
